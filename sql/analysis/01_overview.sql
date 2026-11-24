SELECT MIN(order_date) AS period_start, MAX(order_date) AS period_end,
       COUNT(*) AS orders, COUNT(DISTINCT customer_id) AS purchasing_customers,
       ROUND(SUM(gross_cents)/100.0,2) AS gross_value,
       ROUND(SUM(returned_cents)/100.0,2) AS returned_value,
       ROUND(SUM(retained_cents)/100.0,2) AS retained_value,
       SUM(is_returned) AS returned_orders,
       ROUND(1.0*SUM(is_returned)/COUNT(*),6) AS order_return_rate,
       ROUND(1.0*SUM(returned_cents)/SUM(gross_cents),6) AS value_return_rate,
       COUNT(gross_cents) AS orders_with_lines,
       COUNT(*)-COUNT(gross_cents) AS orders_missing_lines,
       ROUND(SUM(gross_cents)/100.0/COUNT(gross_cents),2) AS gross_aov_priced_orders,
       SUM(before_registration) AS chronology_issues
FROM order_facts;
