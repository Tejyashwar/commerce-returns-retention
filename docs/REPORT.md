# Commerce: Returns & Customer Retention

An independent SQL analysis and Tableau dashboard project using the supplied e-commerce dataset.

Coverage: **2023-04-15 to 2025-04-14**. Snapshot cutoff: **2025-04-14**.

| Metric | Result |
|---|---:|
| Orders | 1,000 |
| Purchasing customers | 199 |
| Gross listed-price value | 2,757,346.10 CU |
| Returned listed-price value | 708,286.76 CU |
| Retained listed-price value | 2,049,059.34 CU |
| Order return rate | 24.9% |
| Value return rate | 25.7% |
| 90-day repeat rate | 44.4% (87/196) |

## Returns absorb a quarter of listed-price value

249 of 1,000 orders are flagged returned (24.9%). Available lines on returned orders represent 708,286.76 CU, or 25.7% of recorded gross listed-price value. Monetary totals cover only 853 orders with lines; 147 orders have unknown amounts.

## Prioritize value exposure and rate separately

Electronics has the largest returned value: 163,791.60 CU. Africa South has the highest order return rate: 31.4% across 102 orders. Rank by both exposure and denominator size before choosing a pilot.

## A repeat customer is not necessarily a recent customer

191 of 199 purchasing customers have more than one observed order (96.0%). Within a comparable 90-day window, 87 of 196 eligible customers repeat (44.4%). These measure different behavior.

## Review established customers who have cooled

32 customers last purchased more than 90 days before the dataset cutoff and have historical retained value at or above the purchasing-customer average. Use these IDs for a small win-back experiment; they are not predicted churn cases.

## Repair chronology before lifecycle reporting

363 orders (36.3%) predate customer registration. Records are flagged and retained, rather than silently repaired. First observed order defines acquisition cohorts; registration-based onboarding conclusions are unsuitable.

## Treat recovery as a scenario, not achieved savings

Preventing 10% of returned listed-price value would preserve 70,828.68 CU over the historical coverage. This is arithmetic sensitivity only; no return reason, campaign effect, cost or profit data supports a forecast.


## Recommended next steps

1. Reconcile customer creation dates with source-system timestamps before lifecycle automation.
2. Audit the top returned-value category and high-rate regions; collect return reasons and invoice prices.
3. Pilot a win-back message on a randomized subset of the review list, with a holdout and margin-aware success criteria.
4. Collect COGS, actual refunds, discounts and campaign costs before estimating profit impact.

## Definitions and limits

147 of 1,000 orders have no lines, including 35 returned orders. Monetary values cover only the 853 orders with recorded lines; missing amounts stay NULL rather than zero. Order return rate and retention use all orders. Prices are the supplied product list prices; no transaction-level sale price exists. Values are quantity × list price, with whole orders excluded when IsReturned=1. They are not accounting revenue, actual refunds, margin, or profit. Currency is unspecified, so CU means currency units. The small dataset is an educational case study; do not generalize results to a live business. Dates span 15 April 2023 to 14 April 2025; both boundary months have partial coverage. Recency is fixed at the dataset cutoff, not today's date. Returns have no event dates, so returned value is assigned to the order month. Observed first purchase can predate the available history; acquisition cohorts are left-censored. Recent customers are excluded from 90-day rates until the full follow-up window is available. No registration date is overwritten.

## Verification

16 checks passed: referential integrity, grain preservation, positive inputs, independent Decimal reconciliation, rollups, 90-day denominators and chronology warnings. See `validation.json` and `QA.md` for the exact coverage, including Tableau verification.

## Dataset attribution

Dataset schema and records: [Simran Subhash Ghag / ecommerce-analysis-sql-capstone](https://github.com/Simranghag22/ecommerce-analysis-sql-capstone), commit `04f0299ce7fdff88f4108a83034510f626f9b261`. The original analysis, findings, report and dashboard were not reused. Source currency and dataset generation method were not documented. See `data/raw/provenance.json` for checksums.
