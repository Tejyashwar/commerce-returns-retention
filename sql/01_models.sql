-- Dialect: SQLite 3.35+. Monetary arithmetic uses integer minor units.
-- Grain: one row per source order line. Source has current product prices only;
-- line value is an estimate at listed price, not an invoice or profit measure.
CREATE VIEW line_items AS
SELECT d.OrderDetailID AS line_id, o.OrderID AS order_id,
       o.CustomerID AS customer_id, o.OrderDate AS order_date,
       o.IsReturned AS is_returned, p.ProductID AS product_id,
       p.ProductName AS product_name, p.Category AS category,
       r.RegionName AS region, r.Country AS country,
       d.Quantity AS quantity, CAST(ROUND(p.Price * 100) AS INTEGER) AS price_cents,
       d.Quantity * CAST(ROUND(p.Price * 100) AS INTEGER) AS gross_cents,
       CASE WHEN o.IsReturned = 1 THEN d.Quantity * CAST(ROUND(p.Price * 100) AS INTEGER) ELSE 0 END AS returned_cents,
       CASE WHEN o.IsReturned = 0 THEN d.Quantity * CAST(ROUND(p.Price * 100) AS INTEGER) ELSE 0 END AS retained_cents,
       CASE WHEN o.OrderDate < c.CreatedAt THEN 1 ELSE 0 END AS before_registration
FROM OrderDetails d
JOIN Orders o ON o.OrderID = d.OrderID
JOIN Products p ON p.ProductID = d.ProductID
JOIN Customers c ON c.CustomerID = o.CustomerID
JOIN Regions r ON r.RegionID = c.RegionID;

-- Aggregate line amounts FIRST so orders are counted exactly once.
CREATE VIEW order_facts AS
WITH line_totals AS (
 SELECT order_id, COUNT(*) AS line_count, SUM(quantity) AS units,
        SUM(gross_cents) AS gross_cents, SUM(returned_cents) AS returned_cents,
        SUM(retained_cents) AS retained_cents
 FROM line_items GROUP BY order_id
)
SELECT o.OrderID AS order_id, o.CustomerID AS customer_id, o.OrderDate AS order_date,
       r.RegionName AS region, r.Country AS country, o.IsReturned AS is_returned,
       CASE WHEN o.OrderDate<c.CreatedAt THEN 1 ELSE 0 END AS before_registration,
       COALESCE(t.line_count,0) AS line_count, t.units,
       t.gross_cents,t.returned_cents,t.retained_cents
FROM Orders o JOIN Customers c ON c.CustomerID=o.CustomerID
JOIN Regions r ON r.RegionID=c.RegionID
LEFT JOIN line_totals t ON t.order_id=o.OrderID;

CREATE VIEW customer_activity AS
WITH sequenced AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS purchase_number,
         LEAD(order_date) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS next_order_date
  FROM order_facts
), summary AS (
  SELECT customer_id, MIN(order_date) AS first_order_date,
         MAX(order_date) AS last_order_date, COUNT(*) AS orders,
         SUM(is_returned) AS returned_orders, SUM(gross_cents) AS gross_cents,
         SUM(retained_cents) AS retained_cents,
         MAX(CASE WHEN purchase_number=1 THEN next_order_date END) AS second_order_date,
         SUM(before_registration) AS chronology_issues
  FROM sequenced GROUP BY customer_id
)
SELECT *, CAST(julianday((SELECT MAX(OrderDate) FROM Orders))-julianday(last_order_date) AS INTEGER) AS recency_days,
       CASE WHEN last_order_date >= date((SELECT MAX(OrderDate) FROM Orders), '-90 days') THEN 'Active: 0-90 days'
            WHEN last_order_date >= date((SELECT MAX(OrderDate) FROM Orders), '-180 days') THEN 'Cooling: 91-180 days'
            ELSE 'Inactive: 181+ days' END AS activity_segment,
       CASE WHEN first_order_date <= date((SELECT MAX(OrderDate) FROM Orders), '-90 days') THEN 1 ELSE 0 END AS eligible_90d,
       CASE WHEN second_order_date <= date(first_order_date, '+90 days') THEN 1 ELSE 0 END AS repeated_90d
FROM summary;
