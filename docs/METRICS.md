# Metric definitions

| Metric | Formula | Grain / denominator |
|---|---|---|
| Gross listed-price value | SUM(quantity × current supplied product list price) | Recorded order lines only |
| Returned value | Gross value for orders with IsReturned = 1 | Entire-order flag; actual refund is unavailable |
| Retained value | Gross value for orders with IsReturned = 0 | Recorded lines, after excluding flagged returns |
| Order return rate | Returned source orders / all source orders | Order grain; 249 / 1,000 |
| Value return rate | Returned recorded value / gross recorded value | Known lines only; not the same population as order rate |
| Priced-order AOV | Gross recorded value / orders with lines | 853 orders; missing orders are excluded, not assigned zero |
| All-time repeat share | Customers with >1 order / purchasing customers | 191 / 199; unequal follow-up |
| 90-day repeat rate | Eligible customers with second order ≤ first + 90 days / eligible customers | Eligibility: first order ≤ cutoff − 90 days; 87 / 196 |
| Recency | Cutoff date − latest observed order date | Cutoff = MAX(OrderDate), 2025-04-14 |
| Win-back review | Recency > 90 days and historical retained value ≥ customer average | Rule-based shortlist, not predicted churn |
| Scenario value preserved | Recorded returned value × assumed reduction fraction | Arithmetic sensitivity, not profit or realized savings |

## Grain and data quality

Source model: Regions → Customers → Orders → OrderDetails ← Products. Prices are converted once to integer cents before multiplication. `line_items` has one row per source line; `order_facts` starts from the complete Orders table and left joins aggregated lines, preserving all 1,000 orders. Unknown missing-line amounts stay NULL. `customer_activity` groups all observed orders, including returned orders and orders without lines. A purchase means an observed order, regardless of returns.

The source has 200 customer records, but only 199 placed an observed order. Non-purchasers do not enter recency or repeat-purchase denominators. Customer-average retained value for the review rule uses SQL AVG over known values.

363 orders precede customer registration. They are kept, flagged and surfaced, with no guessed corrections. Cohorts use first observed order instead. The beginning of the data window can omit earlier purchases, so these are observed-acquisition cohorts rather than proven new-customer cohorts.

Orders are sorted by `(OrderDate, OrderID)` for purchase sequence. Two distinct orders on the same date count as repeat purchasing. The 90th day is inclusive. Customers with fewer than 90 days of follow-up are excluded from both numerator and denominator. No eligible customers means NULL, not 0%.

Monthly value is attributed to order date because return dates are missing. The calendar spine includes all months in the observed span. First and last months are flagged partial. Ratios must be recomputed from numerator/denominator; never sum or take an unweighted average of subgroup rates. Category distinct-order counts overlap and cannot be summed into total orders.

Customer recency labels reflect inactivity at the historical cutoff. They do not prove churn. No product costs, discounts, invoice prices, return reasons, marketing spend or customer lifetime forecasts are available.
