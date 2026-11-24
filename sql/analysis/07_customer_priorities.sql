-- Rule-based review list, not a churn prediction or modeled lifetime value.
SELECT customer_id, first_order_date, last_order_date, recency_days, activity_segment,
       orders, returned_orders, retained_cents/100.0 AS retained_value,
       chronology_issues,
       CASE WHEN recency_days>90 AND retained_cents >= (SELECT AVG(retained_cents) FROM customer_activity)
            THEN 'Review for win-back pilot' ELSE 'Monitor' END AS recommended_action
FROM customer_activity ORDER BY retained_cents DESC,customer_id;
