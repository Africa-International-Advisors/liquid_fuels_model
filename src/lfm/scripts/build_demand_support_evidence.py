"""Summarise registered historical observations for the demand-support exhibit."""
import csv,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'output/delivered/demand_support_2026_10_08'
OUT.mkdir(parents=True,exist_ok=True)
sources=[]
def read(name):
    p=ROOT/'assumptions/2026/timeseries'/name
    sources.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    return list(csv.DictReader(p.open(encoding='utf-8')))
power=read('eskom_fuel_eaf_review_2026_10_07.csv')
freight=read('freight_payload_statssa_review.csv')
macro=read('macro_statssa.csv')
def compare(rows,dimension,key,scale=1):
    chosen=[next(r for r in rows if r['period']==str(y) and r[dimension]==key) for y in [2024,2025]]
    if 'basis' in chosen[0] and dimension=='series':assert all(r['basis']=='actual' for r in chosen)
    a,b=[float(r['value'])/scale for r in chosen]
    return {'start':a,'end':b,'change':b-a,'percent_change':100*(b/a-1),'observations':chosen}
data={'periods':[2024,2025],'power_period':'financial years ending 31 March','freight_sector_period':'calendar years',
      'fuel':compare(power,'series','eskom_ocgt_diesel_and_kerosene'),
      'eaf':compare(power,'series','eskom_eaf'),
      'cost':compare(power,'series','eskom_ocgt_cost_including_storage_demurrage',1000),
      'road':compare(freight,'mode','road',1000),'rail':compare(freight,'mode','rail',1000),
      'agriculture':compare(macro,'series','agriculture_forestry_and_fishing',1e9),
      'mining':compare(macro,'series','mining_and_quarrying',1e9),
      'manufacturing':compare(macro,'series','manufacturing',1e9),'sources':sources}
data['road_share_2025']=100*data['road']['end']/(data['road']['end']+data['rail']['end'])
data['limits']='Own Eskom diesel plus kerosene; cost includes storage/demurrage. Freight uses December 2025 revised vintage for both years. Sector measures are real GVA in 2015 rand, not fuel volumes; no diesel displacement inferred.'
(OUT/'evidence.json').write_text(json.dumps(data,indent=2)+'\n')
