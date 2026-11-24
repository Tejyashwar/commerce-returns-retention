# Tableau workbook and refresh

1. Run `python3 scripts/build.py` from the project root.
2. Open `tableau/Commerce.twbx` in Tableau Desktop. The package contains its CSV sources; no database connection is required.
3. Select `01 Sales and Returns` or `02 Customer Retention` from the tabs. Sixteen underlying worksheets remain editable.
4. To refresh, close the workbook, rebuild, and reopen the regenerated TWBX. SQL logic is authoritative. Changes made only in Tableau are not preserved by the generated-workbook build; save a separate edited copy if you customize it.

The unpackaged `tableau/Commerce.twb` resolves CSVs from its adjacent `Data/` folder. Keep that folder with the TWB. [Tableau's packaged-workbook documentation](https://help.tableau.com/current/pro/desktop/en-us/save_savework_packagedworkbooks.htm) explains how local text sources are bundled.

Sources: overview (one row), monthly (one row/month), category (one row/category), region (one row/region), segments (one row/recency band), repeat_90d (one row/first-order quarter) and retention_summary (one row). Summary rates use SUM only because each chart mark represents exactly one exported row. Do not remove the grouping dimension and SUM subgroup percentages; use the single-row summary source or recompute weighted rates from counts.

These are full-period dashboards with hover and mark selection. No global date/category filter is claimed: independent summary sources have different grains. Null cohort rates indicate insufficient follow-up and must not be converted to zeros.

The SVG in the README is a separate static view of SQL results, not an exported Tableau screenshot. Native Desktop screenshots, where present, are labeled separately in QA documentation. Publishing to Tableau Public or Tableau Cloud is a separate step and has not been performed.
