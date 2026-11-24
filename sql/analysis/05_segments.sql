SELECT activity_segment, COUNT(*) AS customers, SUM(orders) AS orders,
       SUM(retained_cents)/100.0 AS retained_value,
       SUM(gross_cents)/100.0 AS gross_value,
       ROUND(1.0*SUM(returned_orders)/SUM(orders),6) AS order_return_rate,
       ROUND(SUM(retained_cents)/100.0/COUNT(*),2) AS retained_value_per_customer
FROM customer_activity GROUP BY activity_segment ORDER BY activity_segment;
