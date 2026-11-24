-- Calendar spine retains empty months; endpoint months are incomplete coverage.
WITH RECURSIVE months(month) AS (
  SELECT date(MIN(OrderDate),'start of month') FROM Orders
  UNION ALL SELECT date(month,'+1 month') FROM months
  WHERE month < (SELECT date(MAX(OrderDate),'start of month') FROM Orders)
), monthly AS (
  SELECT substr(order_date,1,7) AS month_key, COUNT(*) AS orders,
         SUM(gross_cents) AS gross_cents, SUM(retained_cents) AS retained_cents,
         SUM(returned_cents) AS returned_cents, SUM(is_returned) AS returned_orders
  FROM order_facts GROUP BY substr(order_date,1,7)
)
SELECT m.month AS month, COALESCE(a.orders,0) AS orders,
       COALESCE(a.gross_cents,0)/100.0 AS gross_value,
       COALESCE(a.retained_cents,0)/100.0 AS retained_value,
       COALESCE(a.returned_cents,0)/100.0 AS returned_value,
       ROUND(1.0*a.returned_orders/NULLIF(a.orders,0),6) AS return_rate,
       CASE WHEN m.month IN ((SELECT date(MIN(OrderDate),'start of month') FROM Orders),
                            (SELECT date(MAX(OrderDate),'start of month') FROM Orders))
            THEN 'Partial boundary month' ELSE 'Full calendar month within coverage' END AS coverage
FROM months m LEFT JOIN monthly a ON a.month_key=substr(m.month,1,7) ORDER BY month;
