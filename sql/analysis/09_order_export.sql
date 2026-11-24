-- Order grain: safe for order counts, returns, and region/date filtering in Tableau.
SELECT order_id, customer_id, order_date, region, country, is_returned,
       line_count, units, gross_cents/100.0 AS gross_value,
       returned_cents/100.0 AS returned_value, retained_cents/100.0 AS retained_value,
       before_registration
FROM order_facts ORDER BY order_date,order_id;
