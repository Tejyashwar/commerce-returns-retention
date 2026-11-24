#!/usr/bin/env python3
"""Rebuild the database, SQL exports, report and Tableau package; stdlib only."""
import csv
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def build():
    db = ROOT / 'data/commerce.sqlite'
    db.unlink(missing_ok=True)
    con = sqlite3.connect(db)
    con.execute('PRAGMA foreign_keys=ON')
    con.executescript((ROOT / 'data/raw/source_seed.sql').read_text())
    con.executescript((ROOT / 'sql/01_models.sql').read_text())
    results = {}
    for path in sorted((ROOT / 'sql/analysis').glob('*.sql')):
        cursor = con.execute(path.read_text())
        headers = [d[0] for d in cursor.description]
        rows = cursor.fetchall()
        with (ROOT / 'data/exports' / (path.stem[3:] + '.csv')).open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        results[path.stem[3:]] = [dict(zip(headers, row)) for row in rows]
    from validate import validate
    checks = validate(con, results)
    (ROOT / 'docs/validation.json').write_text(json.dumps(checks, indent=2) + '\n')
    con.commit()
    con.close()
    from build_tableau import build_tableau
    build_tableau(ROOT)
    from report import make_report
    make_report(ROOT, results, checks)
    manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted((ROOT / 'data/exports').glob('*.csv'))}
    (ROOT / 'docs/export_checksums.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'overview': results['overview'][0], 'checks': checks}, indent=2))


if __name__ == '__main__':
    build()
