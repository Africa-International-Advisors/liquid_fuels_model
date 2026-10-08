"""Resolve existing evidence for presentation revisions without changing forecasts."""
import hashlib
import json
from pathlib import Path
import pandas as pd
import yaml
from lfm.model.supply.terminal_handling import annual_handling_m3

def main():
    root=Path(__file__).resolve().parents[3]
    out=root/'output/sa_feedback_2026_10_07'
    out.mkdir(exist_ok=True)
    files=['output/delivered/sa_review_2026_10_07_v3/exhibit_data.csv',
           'assumptions/2026/timeseries/nev_sales_naamsa.csv',
           'assumptions/2026/timeseries/ocgt_generation_eskom.csv',
           'assumptions/2026/timeseries/refinery_capacity_reported.csv',
           'assumptions/2026/terminal_handling.yaml',
           'pptx/story/storage_operator_inventory_2026_10_06.csv']
    frame=pd.read_csv(root/files[0])
    series={}
    for (exhibit,label),g in frame.groupby(['exhibit','series']):
        series.setdefault(exhibit,{})[label]={str(int(r.period)):float(r.value) for r in g.itertuples()}
    metrics={}
    for key,start,end in [('01_demand',2013,2023),('10_trade',2020,2025)]:
        metrics[key]={}
        for label,values in series[key].items():
            if str(start) not in values or str(end) not in values: continue
            a,b=values[str(start)],values[str(end)]
            metrics[key][label]={'start':a,'end':b,'change':b-a,'change_pct':(b/a-1)*100,'cagr_pct':((b/a)**(1/(end-start))-1)*100,'start_year':start,'end_year':end}
    for file,key,labelcol in [(files[1],'ev','drivetrain'),(files[2],'generation','series'),(files[3],'capacity','asset')]:
        data=pd.read_csv(root/file)
        series[key]={label:{str(int(r.period)):float(r.value) for r in group.itertuples()} for label,group in data.groupby(labelcol)}
    turns=yaml.safe_load((root/files[4]).read_text())['monthly_turns']['value']
    inventory=pd.read_csv(root/files[5]); handling={}
    for site in ['Durban','Lesedi']:
        g=inventory[(inventory.operator=='Vopak') & inventory.site.str.contains(site)]
        cap=float(g.gross_capacity_m3.sum())
        assert cap>0,site
        handling[site]={'gross_capacity_m3':cap,'annual_bn_litres':{name:annual_handling_m3(cap,float(t))/1e6 for name,t in turns.items()}}
    result={'series':series,'metrics':metrics,'handling':handling,'monthly_turns':turns,
        'status':'Historical observations plus registered illustrative gross-turn sensitivity; no nine-world calibration',
        'provenance':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files}}
    (out/'data.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'metrics':metrics,'handling':handling},indent=2))

if __name__=='__main__': main()
