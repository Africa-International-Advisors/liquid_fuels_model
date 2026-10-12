"""Synchronise only the October analytical snapshot's owned register rows."""
import csv, hashlib
from pathlib import Path
from lfm.governance import inventory
def main():
    root=Path(__file__).resolve().parents[3];p=root/'governance/assumption_register.csv'
    with p.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    fields=list(rows[0]);rows=[r for r in rows if r['register_group'] not in ('REG-SA-ANALYTICS-202510','REG-SA-STORY-CASE-2025')]
    for r in inventory():
        if r['block'] in ('sa_analytics_2025.snapshot','sa_story_case_2025.production'):
            rows.append({k:('LOC-'+hashlib.sha1(r['assumption'].encode()).hexdigest()[:12] if k=='id' else 'unreviewed' if k=='review_status' else r.get(k,'')) for k in fields})
    with p.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
if __name__=='__main__':main()
