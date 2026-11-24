"""Produce a readable report and SVG overview from executed SQL results."""
from html import escape


def make_report(root, data, checks):
    o=data['overview'][0]; r=data['retention_summary'][0]
    category=data['category'][0]
    region=max(data['region'],key=lambda x:x['order_return_rate'])
    scenario=next(x for x in data['scenarios'] if x['reduction_fraction']==0.1)
    pct=lambda x:f'{x:.1%}'
    money=lambda x:f'{x:,.2f} CU'
    findings=[
      ('Returns absorb a quarter of listed-price value',f"{o['returned_orders']:,} of {o['orders']:,} orders are flagged returned ({pct(o['order_return_rate'])}). Available lines on returned orders represent {money(o['returned_value'])}, or {pct(o['value_return_rate'])} of recorded gross listed-price value. Monetary totals cover only {o['orders_with_lines']} orders with lines; {o['orders_missing_lines']} orders have unknown amounts."),
      ('Prioritize value exposure and rate separately',f"{category['category']} has the largest returned value: {money(category['returned_value'])}. {region['region']} has the highest order return rate: {pct(region['order_return_rate'])} across {region['orders']} orders. Rank by both exposure and denominator size before choosing a pilot."),
      ('A repeat customer is not necessarily a recent customer',f"{r['repeat_customers_all_time']} of {r['purchasing_customers']} purchasing customers have more than one observed order ({pct(r['repeat_share_all_time'])}). Within a comparable 90-day window, {r['repeat_customers_90d']} of {r['eligible_customers_90d']} eligible customers repeat ({pct(r['repeat_rate_90d'])}). These measure different behavior."),
      ('Review established customers who have cooled',f"{r['winback_review_customers']} customers last purchased more than 90 days before the dataset cutoff and have historical retained value at or above the purchasing-customer average. Use these IDs for a small win-back experiment; they are not predicted churn cases."),
      ('Repair chronology before lifecycle reporting',f"{o['chronology_issues']} orders ({pct(o['chronology_issues']/o['orders'])}) predate customer registration. Records are flagged and retained, rather than silently repaired. First observed order defines acquisition cohorts; registration-based onboarding conclusions are unsuitable."),
      ('Treat recovery as a scenario, not achieved savings',f"Preventing 10% of returned listed-price value would preserve {money(scenario['illustrative_value_preserved'])} over the historical coverage. This is arithmetic sensitivity only; no return reason, campaign effect, cost or profit data supports a forecast.")]
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1000" viewBox="0 0 1440 1000">',
         '<rect width="1440" height="1000" fill="#f0f5f7"/>',
         '<rect width="1440" height="140" fill="#122d3f"/>']
    def text(x,y,s,size=16,color='#122d3f',weight='400'):
        svg.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(str(s))}</text>')
    text(35,40,'COMMERCE / RETURNS & RETENTION',14,'#9ad9dc','700')
    text(35,83,'Keep more value. Understand who comes back.',32,'white','700')
    text(35,115,'15 Apr 2023 – 14 Apr 2025 · 1,000 orders · 853 orders with amounts · Currency unspecified (CU)',16,'#cee0e8')
    kpis=[('GROSS LISTED-PRICE VALUE',f"{o['gross_value']/1e6:.3f}m CU"),('RETAINED AFTER RETURNS',f"{o['retained_value']/1e6:.3f}m CU"),('ORDER RETURN RATE',pct(o['order_return_rate'])),('REPEAT WITHIN 90 DAYS',pct(r['repeat_rate_90d']))]
    for i,(label,value) in enumerate(kpis):
        x=30+i*352
        svg.append(f'<rect x="{x}" y="164" width="326" height="110" rx="8" fill="white"/>')
        text(x+18,195,label,12,'#526b7a','700');text(x+18,246,value,31,'#167d8d','700')
    def panel(x,y,w,h,title,subtitle):
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="white"/>')
        text(x+22,y+32,title,19,weight='700');text(x+22,y+57,subtitle,12,'#526b7a')
    panel(30,296,835,300,'Returned value by category','Listed-price exposure, not profit loss · CU')
    cats=data['category'];maximum=max(x['returned_value'] for x in cats)
    for i,row in enumerate(cats):
        y=384+i*33
        text(52,y+5,row['category'],14)
        w=row['returned_value']/maximum*470
        svg.append(f'<rect x="195" y="{y-12}" width="{w:.1f}" height="20" rx="3" fill="#cd5b45"/>')
        text(680,y+5,f"{row['returned_value']:,.0f}",14)
    panel(885,296,525,300,'Recency as of 14 Apr 2025','Customer counts · last observed purchase')
    maxc=max(x['customers'] for x in data['segments'])
    for i,row in enumerate(data['segments']):
        y=398+i*62
        text(907,y-14,row['activity_segment'],14)
        svg.append(f'<rect x="907" y="{y}" width="{row["customers"]/maxc*390:.1f}" height="19" rx="3" fill="#167d8d"/>')
        text(1310,y+16,row['customers'],14,weight='700')
    panel(30,618,835,285,'Monthly value retained after returns','Boundary months are partial; compare full months only · CU')
    monthly=data['monthly'];maximum=max(x['retained_value'] for x in monthly)
    points=[]
    for i,row in enumerate(monthly):
        x=75+i*745/(len(monthly)-1);y=847-row['retained_value']/maximum*135
        points.append(f'{x:.1f},{y:.1f}')
        if i%6==0 or i==len(monthly)-1:text(x-25,882,row['month'],11,'#526b7a')
    svg.append('<polyline points="'+' '.join(points)+'" fill="none" stroke="#167d8d" stroke-width="3"/>')
    text(53,712,f'{maximum/1000:.0f}k',11,'#526b7a');text(53,849,'0',11,'#526b7a')
    panel(885,618,525,285,'Fix the clock before lifecycle claims',f"{o['chronology_issues']} orders occur before registration")
    for y,line in [(719,'147 orders lack lines; amounts stay unknown.'),(753,'90-day repeat: complete observation windows only.'),(787,'Returned flag applies to the entire order.'),(821,'No costs, refund amounts or historical sale prices.'),(855,'All headline totals reconcile to the source records.')]:text(907,y,line,14,'#526b7a')
    text(35,943,'SQL → validated exports → Tableau | Fresh analysis using the supplied Simran Ghag dataset',14,'#526b7a')
    text(35,971,'Static SQL-result overview. The native Tableau workbook contains two dashboards and sixteen worksheets.',13,'#526b7a')
    svg.append('</svg>')
    (root/'docs/overview.svg').write_text('\n'.join(svg))
    limitations='''147 of 1,000 orders have no lines, including 35 returned orders. Monetary values cover only the 853 orders with recorded lines; missing amounts stay NULL rather than zero. Order return rate and retention use all orders. Prices are the supplied product list prices; no transaction-level sale price exists. Values are quantity × list price, with whole orders excluded when IsReturned=1. They are not accounting revenue, actual refunds, margin, or profit. Currency is unspecified, so CU means currency units. The small dataset is an educational case study; do not generalize results to a live business. Dates span 15 April 2023 to 14 April 2025; both boundary months have partial coverage. Recency is fixed at the dataset cutoff, not today's date. Returns have no event dates, so returned value is assigned to the order month. Observed first purchase can predate the available history; acquisition cohorts are left-censored. Recent customers are excluded from 90-day rates until the full follow-up window is available. No registration date is overwritten.'''
    paragraphs='\n'.join(f'## {title}\n\n{body}\n' for title,body in findings)
    md=f'''# Commerce: Returns & Customer Retention

An independent SQL analysis and Tableau dashboard project using the supplied e-commerce dataset.

Coverage: **{o['period_start']} to {o['period_end']}**. Snapshot cutoff: **{o['period_end']}**.

| Metric | Result |
|---|---:|
| Orders | {o['orders']:,} |
| Purchasing customers | {o['purchasing_customers']:,} |
| Gross listed-price value | {money(o['gross_value'])} |
| Returned listed-price value | {money(o['returned_value'])} |
| Retained listed-price value | {money(o['retained_value'])} |
| Order return rate | {pct(o['order_return_rate'])} |
| Value return rate | {pct(o['value_return_rate'])} |
| 90-day repeat rate | {pct(r['repeat_rate_90d'])} ({r['repeat_customers_90d']}/{r['eligible_customers_90d']}) |

{paragraphs}

## Recommended next steps

1. Reconcile customer creation dates with source-system timestamps before lifecycle automation.
2. Audit the top returned-value category and high-rate regions; collect return reasons and invoice prices.
3. Pilot a win-back message on a randomized subset of the review list, with a holdout and margin-aware success criteria.
4. Collect COGS, actual refunds, discounts and campaign costs before estimating profit impact.

## Definitions and limits

{limitations}

## Verification

{checks['passed']} checks passed: referential integrity, grain preservation, positive inputs, independent Decimal reconciliation, rollups, 90-day denominators and chronology warnings. See `validation.json` and `QA.md` for the exact coverage, including Tableau verification.

## Dataset attribution

Dataset schema and records: [Simran Subhash Ghag / ecommerce-analysis-sql-capstone](https://github.com/Simranghag22/ecommerce-analysis-sql-capstone), commit `04f0299ce7fdff88f4108a83034510f626f9b261`. The original analysis, findings, report and dashboard were not reused. Source currency and dataset generation method were not documented. See `data/raw/provenance.json` for checksums.
'''
    (root/'docs/REPORT.md').write_text(md)
    cards=''.join(f'<section><h2>{escape(t)}</h2><p>{escape(b)}</p></section>' for t,b in findings)
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Commerce — Returns & Retention</title><style>body{margin:0;background:#f0f5f7;color:#122d3f;font:17px/1.6 system-ui,sans-serif}main{max-width:1160px;margin:auto;padding:32px}h1{font-size:40px;line-height:1.15}h2{font-size:22px;margin-top:0}p{color:#435c6b}section{padding:25px;background:white;border-radius:12px;margin:18px 0}svg{width:100%;height:auto;border-radius:12px}a{color:#167d8d}.eyebrow{font-size:13px;letter-spacing:2px;color:#167d8d;font-weight:700}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.grid section{margin:0}footer{padding:24px 0;font-size:14px}@media(max-width:760px){.grid{grid-template-columns:1fr}main{padding:16px}}</style><main><div class="eyebrow">SQL + TABLEAU / PROJECT REPORT</div><h1>Returns & Customer Retention</h1><p>Independent analysis of the supplied educational e-commerce dataset. Values shown in currency units (CU), because source currency is unspecified.</p>'''
    html+='\n'.join(svg)+'<div class="grid">'+cards+'</div><section><h2>Definitions and limits</h2><p>'+escape(limitations)+'</p></section><footer>Dataset: <a href="https://github.com/Simranghag22/ecommerce-analysis-sql-capstone">Simran Subhash Ghag</a>. Fresh SQL analysis and Tableau design. <a href="../tableau/Commerce.twbx">Download Tableau workbook</a> · <a href="validation.json">Validation results</a></footer></main></html>'
    (root/'docs/report.html').write_text(html)
