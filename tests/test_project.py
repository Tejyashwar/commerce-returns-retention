import sqlite3
import unittest
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.c=sqlite3.connect(':memory:')
        self.c.executescript((ROOT/'data/raw/source_seed.sql').read_text().split('INSERT INTO')[0])
        self.c.execute("INSERT INTO Regions VALUES(1,'Test','Test')")
        for cid in range(1,5):
            self.c.execute("INSERT INTO Customers VALUES(?, 'Test', '', '', 1, '2020-01-01')",(cid,))
        self.c.execute("INSERT INTO Products VALUES(1,'Test','Test',0.10)")
        orders=[(1,1,'2025-01-02',0),(2,1,'2025-04-02',0),
                (3,2,'2025-01-01',0),(4,2,'2025-04-02',1),
                (5,3,'2025-01-03',0),(6,4,'2025-01-02',0),(7,4,'2025-01-02',0)]
        self.c.executemany('INSERT INTO Orders VALUES(?,?,?,?)',orders)
        # Order 7 intentionally has no lines. Its value must remain NULL.
        for oid in range(1,7):
            self.c.execute('INSERT INTO OrderDetails VALUES(?,?,1,3)',(oid,oid))
        self.c.executescript((ROOT/'sql/01_models.sql').read_text())

    def tearDown(self):
        self.c.close()

    def test_90_day_boundaries_and_same_day_repeat(self):
        rows={r[0]:r[1:] for r in self.c.execute('SELECT customer_id,eligible_90d,repeated_90d FROM customer_activity')}
        self.assertEqual(rows,{1:(1,1),2:(1,0),3:(0,0),4:(1,1)})

    def test_missing_line_order_counted_with_unknown_amount(self):
        self.assertEqual(self.c.execute('SELECT COUNT(*) FROM order_facts').fetchone()[0],7)
        self.assertEqual(self.c.execute('SELECT line_count,gross_cents FROM order_facts WHERE order_id=7').fetchone(),(0,None))

    def test_integer_money_and_order_return_semantics(self):
        self.assertEqual(self.c.execute('SELECT SUM(gross_cents),SUM(returned_cents),SUM(retained_cents) FROM order_facts').fetchone(),(180,30,150))


class PackageTests(unittest.TestCase):
    def test_packaged_data_matches_sql_exports(self):
        with zipfile.ZipFile(ROOT/'tableau/Commerce.twbx') as z:
            wb=ET.fromstring(z.read('Commerce.twb'))
            for cn in wb.findall('datasources/datasource/connection'):
                filename=cn.get('filename')
                self.assertEqual(z.read('Data/'+filename),(ROOT/'data/exports'/filename).read_bytes())
            names={w.get('name') for w in wb.findall('worksheets/worksheet')}
            self.assertEqual(len(names),16)
            self.assertEqual(len(wb.findall('dashboards/dashboard')),2)
            for zone in wb.findall('dashboards/dashboard/zones/zone'):
                if zone.get('name'):
                    self.assertIn(zone.get('name'),names)

    def test_no_absolute_or_external_connection(self):
        wb=ET.parse(ROOT/'tableau/Commerce.twb')
        for cn in wb.findall('datasources/datasource/connection'):
            self.assertEqual(cn.get('class'),'textscan')
            self.assertEqual(cn.get('directory'),'Data')


if __name__=='__main__':
    unittest.main()
