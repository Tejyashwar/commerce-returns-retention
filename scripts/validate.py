"""Reconciliation against raw records, independent Decimal arithmetic and dates."""
from collections import defaultdict
from datetime import date
from decimal import Decimal


def validate(con, results):
    checks = []
    def check(name, passed):
        checks.append({'check': name, 'status': 'PASS' if passed else 'FAIL'})
        if not passed:
            raise AssertionError(name)
    check('Foreign key integrity', not con.execute('PRAGMA foreign_key_check').fetchall())
    check('Database integrity', con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok')
    check('Order and line grain preserved',
          con.execute('SELECT COUNT(*) FROM order_facts').fetchone()[0] == con.execute('SELECT COUNT(*) FROM Orders').fetchone()[0]
          and con.execute('SELECT COUNT(*) FROM line_items').fetchone()[0] == con.execute('SELECT COUNT(*) FROM OrderDetails').fetchone()[0])
    missing = con.execute('SELECT COUNT(*) FROM Orders WHERE OrderID NOT IN (SELECT OrderID FROM OrderDetails)').fetchone()[0]
    check('Missing-line orders retained with unknown amounts', con.execute('SELECT COUNT(*) FROM order_facts WHERE line_count=0 AND gross_cents IS NULL').fetchone()[0] == missing)
    check('Positive prices and quantities; binary return flag', con.execute('SELECT COUNT(*) FROM line_items WHERE price_cents<=0 OR quantity<=0 OR is_returned NOT IN (0,1)').fetchone()[0] == 0)
    products = {p: Decimal(str(price)) for p, price in con.execute('SELECT ProductID, Price FROM Products')}
    orders = {o: (c, date.fromisoformat(d), r) for o, c, d, r in con.execute('SELECT OrderID, CustomerID, OrderDate, IsReturned FROM Orders')}
    gross = Decimal(0)
    returned = Decimal(0)
    for _, oid, pid, qty in con.execute('SELECT * FROM OrderDetails'):
        amount = products[pid] * qty
        gross += amount
        if orders[oid][2]:
            returned += amount
    o = results['overview'][0]
    check('Gross value reconciles to independent Decimal raw-line sum', Decimal(str(o['gross_value'])) == gross)
    check('Returned value reconciles to raw order flags', Decimal(str(o['returned_value'])) == returned)
    check('Gross = retained + returned to the cent', Decimal(str(o['retained_value'])) + returned == gross)
    for key in ['monthly', 'category', 'region', 'segments']:
        check(f'{key} retained value reconciles', sum(Decimal(str(x['retained_value'])) for x in results[key]) == gross-returned)
    customer_dates = defaultdict(list)
    for oid, (cid, d, _) in orders.items():
        customer_dates[cid].append((d, oid))
    cutoff = max(v[1] for v in orders.values())
    eligible = repeat = 0
    for values in customer_dates.values():
        ds = sorted(values)
        if (cutoff-ds[0][0]).days >= 90:
            eligible += 1
            repeat += int(len(ds)>1 and (ds[1][0]-ds[0][0]).days<=90)
    check('90-day eligible population independently reconciles', sum(x['eligible_customers'] for x in results['repeat_90d']) == eligible)
    check('90-day repeat numerator independently reconciles', sum(x['repeat_customers_90d'] for x in results['repeat_90d']) == repeat)
    check('Ratios bounded and eligible repeat count valid', all(x['repeat_customers_90d']<=x['eligible_customers'] for x in results['repeat_90d']))
    dates = {cid: date.fromisoformat(d) for cid,d in con.execute('SELECT CustomerID, CreatedAt FROM Customers')}
    bad = sum(d<dates[cid] for cid,d,_ in orders.values())
    check('Chronology warning independently reconciles', bad == o['chronology_issues'])
    return {'engine': 'SQLite ' + __import__('sqlite3').sqlite_version,
            'passed': len(checks), 'failed': 0, 'checks': checks,
            'warnings': [{'issue': 'Orders before registration', 'count': bad,
                          'treatment': 'Retained and flagged. Registration cohorts not used.'},
                         {'issue': 'Orders without order lines', 'count': missing,
                          'treatment': 'Included in order and customer counts. Amounts remain NULL; value metrics cover recorded lines only.'}],
            'tableau': 'XML/package checks run by tests/test_project.py; native Desktop verification recorded in docs/QA.md.'}
