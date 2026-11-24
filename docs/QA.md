# Verification

Verified on 24 November 2026.

## Data and SQL

`python3 scripts/build.py` completes using SQLite 3.50.4. All **16 reconciliation and quality-handling checks pass**. `validation.json` records each result. Gross, returned and retained values were independently recalculated from raw order lines using Python Decimal arithmetic. Monthly, category, region and recency-segment retained values reconcile to the same total.

Raw Orders are retained even when no lines exist. The 147 missing-line orders retain NULL monetary values, and the 363 orders before registration remain flagged. These are source defects, not failed processing checks. No guessed repairs or replacement values were introduced.

`python3 -m unittest discover -s tests -v` passes **five tests**. Fixtures exercise repeat purchasing exactly on day 90, on day 91, same-day repeat orders, incomplete follow-up, missing lines, integer money and whole-order returns. Package tests check embedded CSV byte equality with SQL exports, all 16 worksheet/dashboard references and relative local source connections.

## Visual and native verification

The workbook was loaded in **Tableau Desktop 2026.3 on macOS**. Initial schema compatibility errors were corrected. Both native dashboards render from the embedded CSVs without database credentials. Headline values visible in Desktop match the SQL exports: sales 2,757,346.10 / 2,049,059.34 / 708,286.76 CU and 24.9%; retention 199 customers, 44.4% repeat and 196 eligible customers. The retention dashboard was also opened from a temporary package with that tab selected first; only window-tab order differed from the deliverable. The recent 2025-Q1 cohort correctly displays no rate (one NULL), because follow-up is incomplete. The dashboard canvas is 1100 × 700; a smaller editing window can require scrolling. Date axes use typed dates rather than truncated text labels.

The standalone HTML report was rendered in headless Chrome at 1440 pixels wide and visually inspected. Its overview, finding cards and limitations are readable without clipping. `overview.svg` is a static SQL-result graphic, not a Tableau export. `tableau-sales.png` is a capture of the native Tableau workbook window.

## Scope and remaining limitations

No Tableau Public or Cloud publication was performed. Workbooks use local CSV sources and full-period summaries; there is no shared global filter. This is a historical educational dataset with incomplete amounts, uncertain currency and list prices instead of invoice prices. Monetary results should be described as recorded listed-price values. Return-reduction scenarios are illustrative, and recency rules do not establish causal churn or achieved savings.
