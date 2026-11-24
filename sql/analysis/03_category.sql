SELECT category, COUNT(DISTINCT order_id) AS orders_with_category,
       COUNT(DISTINCT CASE WHEN is_returned=1 THEN order_id END) AS returned_orders,
       SUM(quantity) AS units,
       SUM(gross_cents)/100.0 AS gross_value,
       SUM(returned_cents)/100.0 AS returned_value,
       SUM(retained_cents)/100.0 AS retained_value,
       ROUND(1.0*SUM(returned_cents)/SUM(gross_cents),6) AS value_return_rate,
       DENSE_RANK() OVER (ORDER BY SUM(returned_cents) DESC) AS returned_value_rank
FROM line_items GROUP BY category ORDER BY returned_value DESC;
