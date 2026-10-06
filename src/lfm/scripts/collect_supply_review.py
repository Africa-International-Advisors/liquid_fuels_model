"""Extract staged supply-review observations; never calibrate the model implicitly.

Run after downloading the preserved reports listed in the raw manifest.
All figures retain their published basis. Report dashes are recorded separately
from observed zero capacity. No domestic output is inferred from sales minus trade.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
import shutil
from pypdf import PdfReader


def write_csv(path, rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def extract_trade(reader):
    imports=reader.pages[12].extract_text()
    exports=reader.pages[13].extract_text()
    # Require the source sentences before accepting transcribed rounded numbers.
    for token in ('10.8 billion litres','12.8 billion litres','4 billion litres','4.5 billion'):
        assert token in imports,token
    for token in ('920 million litres','790 million litres','935 million litres','479 million','452 million'):
        assert token in exports,token
    rows=[]
    values={2023:{'petrol':(4.5e9,1.0e9),'diesel':(12.8e9,.935e9),'jet':(.674e9,.452e9)},
            2024:{'petrol':(4e9,.920e9),'diesel':(10.8e9,.790e9),'jet':(.718e9,.479e9)}}
    for year,products in values.items():
        for product, pair in products.items():
            for flow,value in zip(('import','export'),pair):
                rows.append(dict(country='ZAF',period=year,scenario='shared',product=product,
                                 flow=flow,value=value,unit='litres',source_file='trade2024.pdf',
                                 pdf_page=13 if flow=='import' else 14,
                                 precision='rounded narrative; not raw customs extract'))
    return rows


def extract_capacity(reader):
    page=reader.pages[48].extract_text()
    assert 'Capacity of South African refineries' in page
    rows=[]
    for asset in ('Sapref','Enref','Astron Energy','Natref','Sasol','PetroSA'):
        row=next(line for line in page.splitlines() if line.startswith(asset))
        tokens=re.findall(r'\d{2,3}\s+000|(?<!\w)[-–](?!\w)',row)
        assert len(tokens)==10,(asset,tokens)
        for year,token in zip(range(2016,2026),tokens):
            dash=token in ('-','–')
            rows.append(dict(country='ZAF',period=year,scenario='shared',asset=asset,
                             value=0 if dash else int(token.replace(' ','')),unit='bbl/day',
                             basis='crude equivalent' if asset in ('Sasol','PetroSA') else 'nameplate',
                             report_cell='dash; excluded from reported total' if dash else 'numeric',
                             source_file='annual-report-2025.pdf',pdf_page=49))
    for year,total in zip(range(2016,2026),(718000,)*5+(538000,)+(358000,)*4):
        assert sum(r['value'] for r in rows if r['period']==year)==total
    return rows


def main():
    root=Path(__file__).resolve().parents[3]
    raw=root/'external/data/raw/fuel_supply_review_20261006'
    original=root/'external/data/refresh_20261005/raw/fiasa/annual-report-2025.pdf'
    if not (raw/original.name).exists():shutil.copy2(original,raw/original.name)
    out=root/'assumptions/2026/timeseries'
    trade=extract_trade(PdfReader(str(raw/'trade2024.pdf')))
    capacity=extract_capacity(PdfReader(str(raw/original.name)))
    write_csv(out/'fuel_trade_department_review.csv',trade)
    write_csv(out/'refinery_capacity_reported.csv',capacity)
    old=list(csv.DictReader((out/'fuel_trade_fiasa.csv').open(encoding='utf-8-sig')))
    flags=[]
    for new in trade:
        match=next((r for r in old if r['period']==str(new['period']) and r['product']==new['product'] and r['flow']==new['flow']),None)
        if match:
            flags.append(dict(period=new['period'],product=new['product'],flow=new['flow'],
                              old_source='FIASA staged / report 2025',old_value=match['value'],
                              new_source='Government Energy Trade Report 2024',new_value=new['value'],
                              delta=new['value']-float(match['value']),unit='litres',
                              status='source disagreement' if new['value']!=float(match['value']) else 'same rounded value',
                              action='retain both; reconcile raw SARS product coverage and publication vintage',
                              owner='Manish; Nigel review'))
    review=root/'output/delivered/supply_review_2026_10_06';review.mkdir(parents=True,exist_ok=True)
    write_csv(review/'trade_source_flags.csv',flags)
    manifest=json.loads((raw/'manifest.json').read_text())
    meta=dict(retrieved='2026-10-06',status='staged reporting evidence; unreviewed; not consumed by engine',
              sources=manifest,capacity_source=dict(file=original.name,pdf_page=49,
              index='https://fuelsindustry.org.za/publications/annual-reports/',sha256=hashlib.sha256((raw/original.name).read_bytes()).hexdigest()),
              refresh='Download the next government trade report and FIASA annual report; rerun this extractor. Source changes require deliberate register reconciliation.',
              limitations=['Trade values are rounded narrative figures.',
              'Capacity table includes crude-equivalent synthetic plants and idle nameplate capacity; not actual production or usable annual capacity.',
              '2024 source disagreement is retained; no adoption decision or validation inferred.',
              'Official balance index ends at 2021; no recent complete production/export/stock reconciliation established.',
              '2025 preliminary reports and TNPA raw PDF downloads failed in this collection; see manifest.'])
    (out/'supply_review.sources.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print('Extracted',len(trade),'rounded trade observations and',len(capacity),'capacity cells; flags:',review)


if __name__=='__main__':main()
