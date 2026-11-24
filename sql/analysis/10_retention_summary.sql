SELECT COUNT(*) AS purchasing_customers,
       SUM(CASE WHEN orders>1 THEN 1 ELSE 0 END) AS repeat_customers_all_time,
       ROUND(1.0*SUM(CASE WHEN orders>1 THEN 1 ELSE 0 END)/COUNT(*),6) AS repeat_share_all_time,
       SUM(eligible_90d) AS eligible_customers_90d,
       SUM(CASE WHEN eligible_90d=1 THEN repeated_90d ELSE 0 END) AS repeat_customers_90d,
       ROUND(1.0*SUM(CASE WHEN eligible_90d=1 THEN repeated_90d ELSE 0 END)/NULLIF(SUM(eligible_90d),0),6) AS repeat_rate_90d,
       SUM(CASE WHEN recency_days>90 AND retained_cents >= (SELECT AVG(retained_cents) FROM customer_activity) THEN 1 ELSE 0 END) AS winback_review_customers
FROM customer_activity;
