"""Build an evidence-backed screening baseline and explicit calibration handoff.

Source observations are resolved here; calculation functions remain in model/.
No missing commercial input is filled with zero or an invented share.
"""
import csv
import hashlib
import html
import json
from pathlib import Path
import pandas as pd
import yaml
from lfm.model.investment_bridge import balance_residual, required_monthly_turns
from lfm.model.supply.terminal_handling import annual_handling_m3
from lfm.reporting.sa_review import complete_period_totals

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'output/delivered/investment_bridge_2026_10_08'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    cfg=ROOT/'assumptions/2026/investment_bridge.yaml'
    refs=yaml.safe_load(cfg.read_text())['evidence']['value']
    sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in refs.values()}
    sources[cfg.relative_to(ROOT).as_posix()]=hashlib.sha256(cfg.read_bytes()).hexdigest()
    frames={k:pd.read_csv(ROOT/p) for k,p in refs.items() if p.endswith('.csv')}
    scope=yaml.safe_load((ROOT/refs['scope']).read_text())['lesedi_catchment']['value']
    products=('petrol','diesel')
    sales=frames['national_sales']
    sales=sales[(sales.unit=='litres')&(sales.quarters_reported==4)]
    q=frames['provincial_quarters']
    gp={p:complete_period_totals(q[(q.province==scope)&(q['product']==p)],periods_per_year=4) for p in products}
    trade=frames['trade']
    trade=trade[(trade.unit=='litres')&(trade.months_reported==12)]
    candidates=set.intersection(*(set(gp[p]) for p in products),
        *(set(sales[sales['product']==p].period) for p in products),
        *(set(trade[(trade['product']==p)&(trade.flow==f)].period) for p in products for f in ('import','export')))
    year=int(max(candidates))
    def one(frame, **filters):
        sub=frame
        for key,value in filters.items():sub=sub[sub[key]==value]
        if len(sub)!=1:raise ValueError(f'Expected one observation: {filters}, found {len(sub)}')
        return float(sub.iloc[0]['value'])
    latest=[]
    for p in products:
        demand=one(sales,product=p,period=year)
        imp=one(trade,product=p,flow='import',period=year)
        exp=one(trade,product=p,flow='export',period=year)
        latest.append({'year':year,'product':p,'national_sales_bn_l':demand/1e9,
            'gauteng_sales_bn_l':gp[p][year]/1e9,'imports_bn_l':imp/1e9,'exports_bn_l':exp/1e9,
            'sales_less_net_imports_bn_l':-balance_residual(production=0,imports=imp,exports=exp,consumption=demand)['before_stock']/1e9,
            'status':'Residual is NOT measured production; stock, product and customs coverage unresolved'})
    bal=frames['energy_balance']
    fields=('production','imports','exports','final_consumption','statistical_difference')
    years=set.intersection(*(set(bal[(bal['product']==p)&(bal.flow_key==f)&(bal.unit=='litres')].period) for p in products for f in fields))
    byear=int(max(years)); historical=[]
    for p in products:
        vals={f:one(bal,product=p,period=byear,flow_key=f,unit='litres')/1e9 for f in fields}
        assert vals['exports']<=0, 'Source exports are signed outflows'
        r=balance_residual(production=vals['production'],imports=vals['imports'],exports=-vals['exports'],consumption=vals['final_consumption'])
        historical.append({'year':byear,'product':p,**vals,'residual_before_stat_difference_bn_l':r['before_stock'],
            'residual_after_reported_stat_difference_bn_l':r['before_stock']+vals['statistical_difference'],
            'sales_vs_final_consumption_bn_l':one(sales,product=p,period=byear)/1e9-vals['final_consumption'],
            'status':'Source diagnostic only: statistical difference is not a measured stock change'})
    inventory=frames['terminals']; turns=yaml.safe_load((ROOT/refs['turns']).read_text())['monthly_turns']['value']
    screens=[]
    for site in ('Durban','Lesedi'):
        cap=float(inventory[(inventory.operator=='Vopak')&(inventory.site==site)].gross_capacity_m3.sum())
        screens.append({'site':site,'gross_capacity_m3':cap,
            'gross_monthly_turns_per_bn_litres':required_monthly_turns(annual_m3=1e6,capacity_m3=cap),
            'annual_bn_l_by_registered_turns':{k:annual_handling_m3(cap,v)/1e6 for k,v in turns.items()},
            'status':'Gross capacity scale only; working capacity and operating constraints unknown'})
    routes=json.loads((ROOT/refs['routes']).read_text())
    route_rows=[]
    for r in routes:
        route_rows.append({'origin':r['origin'],'destination':r['destination'],'mode':'road',
            'connectivity_distance_km':r['length_m']/1000,'delivered_cost_zar_m3':None,
            'accessible_capacity_m3':None,'status':'Connectivity diagnostic only; no competitive ranking or tanker access validation'})
    for origin,mode in [('Durban','pipeline'),('Durban','rail'),('Secunda','unvalidated'),('Natref','unvalidated')]:
        route_rows.append({'origin':origin,'destination':'Gauteng customer destination to confirm','mode':mode,
            'connectivity_distance_km':None,'delivered_cost_zar_m3':None,'accessible_capacity_m3':None,
            'status':'Matched cost, service and customer access required'})
    worlds=[{'demand':d,'supply':s,'baseline':d==s=='Medium','imports_m3':None,
        'captured_durban_m3':None,'captured_lesedi_m3':None,'required_turns':None,
        'capacity_headroom_m3':None,'investment_option':None,'return':None,
        'status':'Await annual product paths; T1-T5/F1 inputs. No probability assigned'}
        for d in ('Low','Medium','High') for s in ('High','Medium','Low')]
    data={'status':'Implemented screening tools and partial baseline; NOT calibrated investment results',
        'latest_common_sales_trade_year':year,'historical_balance_year':byear,'baseline':latest,
        'historical_balance_diagnostic':historical,'terminal_screens':screens,'routes':route_rows,
        'nine_worlds':worlds,'source_hashes':sources}
    (OUT/'evidence.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    for name,rows in [('baseline',latest),('historical_balance',historical),('route_readiness',route_rows),('nine_worlds',worlds)]:
        with (OUT/f'{name}.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    sections=[]
    for title,rows in [('Matched-year demand and trade',latest),('Historical balance diagnostic',historical),('Terminal gross-turn scale',screens),('Route readiness',route_rows),('Nine-world results: not yet populated',worlds)]:
        df=pd.DataFrame(rows).fillna('Unknown / not calculated')
        sections.append('<h2>'+html.escape(title)+'</h2>'+df.to_html(index=False,escape=True))
    links='<p><a href="data_request.csv">Detailed data request</a> · <a href="collection_templates/">Collection tables</a> · <a href="../../../workstreams/WS0_governance/workplan/sa_investment_bridge_2026_10_08.csv">Implementation log</a> · <a href="evidence.json">Evidence and source hashes</a></p>'
    (OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Investment bridge</title><style>body{font:15px Arial;margin:35px;color:#222}h1,h2{color:#0a2373}table{border-collapse:collapse;font-size:12px;width:100%}td,th{border-bottom:1px solid #ddd;padding:10px;text-align:left;vertical-align:top}h2{margin-top:40px}</style><h1>Six-step investment bridge — 8 October 2026</h1><p>Screening evidence, explicit-input calculation tools and unfilled commercial outputs. No route winner, Vopak share or investment return is asserted.</p>'+links+'<p>2021 energy-balance final consumption differs from sales. The later 2022 residual is not production. Do not infer provincial supply origins from either.</p>'+''.join(sections),encoding='utf-8')
    print(json.dumps({'year':year,'balance_year':byear,'baseline':latest,'historical':historical,'terminal_screens':screens},indent=2))


if __name__=='__main__':main()
