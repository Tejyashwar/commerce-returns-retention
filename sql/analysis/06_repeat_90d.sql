-- A customer is eligible only after a complete 90-day observation window.
WITH cohorts AS (
  SELECT *, substr(first_order_date,1,4)||'-Q'||
    CAST((CAST(strftime('%m',first_order_date) AS INTEGER)+2)/3 AS INTEGER) AS acquisition_quarter
  FROM customer_activity
)
SELECT acquisition_quarter, COUNT(*) AS customers,
       SUM(eligible_90d) AS eligible_customers,
       SUM(CASE WHEN eligible_90d=1 THEN repeated_90d ELSE 0 END) AS repeat_customers_90d,
       ROUND(1.0*SUM(CASE WHEN eligible_90d=1 THEN repeated_90d ELSE 0 END)/NULLIF(SUM(eligible_90d),0),6) AS repeat_rate_90d
FROM cohorts GROUP BY acquisition_quarter ORDER BY acquisition_quarter;
