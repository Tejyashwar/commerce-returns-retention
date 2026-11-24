-- Illustrative value preserved if 5%, 10%, or 20% of returned value is prevented.
-- No claim of causal uplift, realized savings, or profit. Costs are unavailable.
WITH rates(reduction_fraction) AS (VALUES(0.05),(0.10),(0.20))
SELECT reduction_fraction,
       ROUND(SUM(returned_cents)/100.0,2) AS baseline_returned_value,
       ROUND(SUM(returned_cents)/100.0*reduction_fraction,2) AS illustrative_value_preserved
FROM order_facts CROSS JOIN rates GROUP BY reduction_fraction ORDER BY reduction_fraction;
