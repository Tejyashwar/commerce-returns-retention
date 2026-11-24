SELECT region, country, COUNT(*) AS orders, SUM(is_returned) AS returned_orders,
       SUM(gross_cents)/100.0 AS gross_value, SUM(returned_cents)/100.0 AS returned_value,
       SUM(retained_cents)/100.0 AS retained_value,
       ROUND(1.0*SUM(is_returned)/COUNT(*),6) AS order_return_rate,
       ROUND(1.0*SUM(returned_cents)/SUM(gross_cents),6) AS value_return_rate
FROM order_facts GROUP BY region,country ORDER BY returned_value DESC;
