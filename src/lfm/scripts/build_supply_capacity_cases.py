"""Resolve registered capacity inputs and export reporting sensitivities."""
import csv
import hashlib
import json
from pathlib import Path
import yaml
from lfm.governance import inventory, read_rows
from lfm.model.supply.capacity_sensitivity import capacity_case

ROOT=Path(__file__).resolve().parents[3]
base=ROOT/'assumptions/2026'
inputs=[base/'timeseries/refinery_capacity_reported.csv',base/'review_capacity_scenarios.yaml',base/'review_supply_worlds.yaml']
rows=list(csv.DictReader(inputs[0].open(encoding='utf-8-sig')))
history={}
for r in rows:
    history.setdefault(int(r['period']),{})[r['asset']]=float(r['value'])
latest=max(history)
settings=yaml.safe_load(inputs[1].read_text())['capacity_comparison']['value']
cases=yaml.safe_load(inputs[2].read_text())['capacity_cases']['value']
result={name:capacity_case(history[latest],v['excluded_assets'],settings['proposed_addition_bpd'],v['include_sapref_proposal']) for name,v in cases.items()}
out=ROOT/'output/delivered/supply_capacity_cases_2026_10_08'
out.mkdir(parents=True,exist_ok=True)
payload={'history_bpd':history,'cases_bpd':result,'totals_bpd':{k:sum(v.values()) for k,v in result.items()},'latest_year':latest,'horizon_year':settings['horizon_year'],'fid_year':settings['illustrative_fid_year'],'construction_months':settings['construction_months'],'addition_year':settings['illustrative_fid_year']+settings['construction_months']/12,'status':'Illustrative capacity sensitivities, not approved L/M/H fuel-output paths. Low Natref unavailability is hypothetical, not a closure forecast.','provenance':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}}
(out/'data.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
# Register only the newly authored sensitivity block; preserve existing rows.
path=ROOT/'governance/assumption_register.csv'
register=read_rows(path); known={r['assumption'] for r in register}
with path.open('a',encoding='utf-8',newline='') as stream:
    writer=csv.DictWriter(stream,fieldnames=list(register[0]))
    for item in inventory():
        if item['block'].startswith('review_supply_worlds.') and item['assumption'] not in known:
            row={k:item.get(k,'') for k in register[0]}
            row.update(id='LOC-'+hashlib.sha256(item['assumption'].encode()).hexdigest()[:12],reviewer='',review_status='unreviewed')
            writer.writerow(row)
print(json.dumps(payload['totals_bpd']))
