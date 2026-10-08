"""Resolve reported context and registered authored assumptions for a worked case."""
from copy import deepcopy
import csv,hashlib,html,json
from pathlib import Path
import yaml
from lfm.model.illustrative_investment import evaluate_case,reversal_volume

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'output/delivered/vopak_illustration_2026_10_08'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=ROOT/'assumptions/2026/vopak_investment_illustration.yaml'
    cfg=yaml.safe_load(source.read_text());reported=cfg['reported']['value'];a=cfg['illustrative']['value']
    worlds=[]
    for d in ('Low','Medium','High'):
        for s in ('High','Medium','Low'):
            worlds.append(dict(demand_world=d,supply_world=s,**evaluate_case(reported,a,demand_bn_l=a['demand_bn_l'][d],domestic_bn_l=a['domestic_deliveries_bn_l'][s])))
    anchor=worlds[-1]
    shocks=[('Base illustration',{}),('Capex +25%',{'access_package_capex_zar':a['access_package_capex_zar']*a['capex_stress_multiplier'],'tank_addition_capex_zar':a['tank_addition_capex_zar']*a['capex_stress_multiplier']}),
            ('No chargeable excess services',{'excess_service_contribution_zar_m3':a['service_stress_contribution_zar_m3']}),
            ('Vopak gateway capture 60%',{'vopak_share_of_durban_imports':a['capture_stress_vopak_share']})]
    sensitivity=[]
    for label,updates in shocks:
        c={**a,**updates};result=evaluate_case(reported,c,demand_bn_l=a['demand_bn_l']['High'],domestic_bn_l=a['domestic_deliveries_bn_l']['Low'])
        sensitivity.append({'case':label,**result})
    # Scale both origin streams to reduce captured volume exactly, retaining mix.
    reduced={**a,'lesedi_share_of_vopak_flow':a['lesedi_share_of_vopak_flow']*a['volume_stress_multiplier'],
             'lesedi_domestic_capture_share':a['lesedi_domestic_capture_share']*a['volume_stress_multiplier']}
    sensitivity.append({'case':'Captured volume -10%',**evaluate_case(reported,reduced,demand_bn_l=a['demand_bn_l']['High'],domestic_bn_l=a['domestic_deliveries_bn_l']['Low'])})
    thresholds={}
    for label,opta,optb in [('improvement_vs_existing','Existing','Improve access / dispatch'),('tanks_vs_improvement','Improve access / dispatch','Improve + add tanks')]:
        thresholds[label]=reversal_volume(reported,a,domestic_bn_l=a['domestic_deliveries_bn_l']['Low'],
            lower_demand_bn_l=a['demand_bn_l']['Low'],upper_demand_bn_l=a['demand_bn_l']['High'],option_a=opta,option_b=optb)
    inferred={'group_revenue_per_proportional_capacity_eur_year':reported['group_2025_proportional_revenue_eur_m']/reported['group_2025_proportional_capacity_m3_m'],
              'consolidated_storage_revenue_share':reported['group_2025_storage_revenue_eur_m']/reported['group_2025_consolidated_revenue_eur_m'],
              'limits':'Group revenue divided by year-end proportional capacity is a mixed-portfolio intensity, NOT a tariff or site estimate. Occupancy is NOT tank turnover. Sector investment multiples and group operating cash return are NOT South Africa project hurdle rates.'}
    paths=[source,ROOT/reported['annual_report'],ROOT/reported['analyst_presentation'],ROOT/'src/lfm/model/illustrative_investment.py']
    data={'status':'ILLUSTRATIVE ONLY — not Vopak forecasts, contracts, project quotes or investment approval',
          'basis':'100% Lesedi project, pre-tax unlevered constant-ZAR; capex at t0; operating ramp 50/75/100%; no tax/working capital/construction delay/inflation/residual value; selected packages only',
          'reported':reported,'inferred':inferred,'assumptions':a,'worlds':worlds,'anchor':anchor,
          'sensitivity':sensitivity,'reversal_captured_m3':thresholds,
          'provenance':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
          'urls':['https://www.vopak.com/system/files/Vopak_Annual_Report_2025.pdf',
                  'https://www.vopak.com/system/files/Analyst%20presentation%20FY%202025_0.pdf',
                  'https://www.vopak.com/our-terminals?language_content_entity=en']}
    (OUT/'results.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    def write_csv(name,rows):
        with (OUT/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    write_csv('nine_worlds.csv',[{k:r[k] for k in ['demand_world','supply_world','demand_bn_l','domestic_bn_l','captured_lesedi_m3','capture_share_of_catchment','required_monthly_turns','preferred_option','preferred_npv_zar']} for r in worlds])
    write_csv('option_cases.csv',[{'demand_world':r['demand_world'],'supply_world':r['supply_world'],**{k:v for k,v in o.items() if k!='cashflows'}} for r in worlds for o in r['options']])
    write_csv('cashflows.csv',[{'demand_world':r['demand_world'],'supply_world':r['supply_world'],'option':o['option'],'year':i,'incremental_pre_tax_cashflow_zar':v} for r in worlds for o in r['options'] for i,v in enumerate(o['cashflows'])])
    write_csv('sensitivities.csv',[{'case':r['case'],'captured_lesedi_m3':r['captured_lesedi_m3'],'preferred_option':r['preferred_option'],**{o['option']+'_npv_zar':o['npv_zar'] for o in r['options']}} for r in sensitivity])
    write_csv('input_classification.csv',[
        *[dict(classification='REPORTED',input=k,value=json.dumps(v),source=cfg['reported']['source']) for k,v in reported.items()],
        *[dict(classification='INFERRED',input=k,value=str(v),source='Calculated from reported group metrics; not a site estimate') for k,v in inferred.items()],
        *[dict(classification='ILLUSTRATIVE',input=k,value=json.dumps(v),source=cfg['illustrative']['source']) for k,v in a.items()]])
    def table(headers,rows):
        return '<table><tr>'+''.join('<th>'+html.escape(h)+'</th>' for h in headers)+'</tr>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table>'
    body='<h1>Lesedi investment illustration</h1><p class="flag">ILLUSTRATIVE VALUES — not an investment recommendation</p><p>'+html.escape(data['basis'])+'</p>'
    body+='<p>Reported facts: Lesedi 140,000 m³; Vopak ownership 70%; 2025 storage-service revenue '+f"{100*inferred['consolidated_storage_revenue_share']:.1f}%"+' of consolidated revenue. The annual report confirms Lesedi expansion was commissioned in 2025. Physical throughput is never multiplied by ownership.</p>'
    body+='<p>Inferred group revenue intensity: EUR '+f"{inferred['group_revenue_per_proportional_capacity_eur_year']:.1f}"+'/m³/year. This mixed-portfolio ratio is not used as a Lesedi tariff. Authored storage rent is R1,500/gross m³/year; net excess-service contribution is R60/extra m³ only where chargeable separately from rental.</p>'
    body+='<h2>Nine illustrative worlds</h2>'+table(['Demand / supply','Captured bn L/year','Required monthly turns','Preferred package','Incremental NPV Rm'],[[r['demand_world']+' / '+r['supply_world'],f"{r['captured_lesedi_m3']/1e6:.2f}",f"{r['required_monthly_turns']:.2f}",r['preferred_option'],f"{r['preferred_npv_zar']/1e6:.1f}"] for r in worlds])
    body+='<h2>High demand / low domestic deliveries: options</h2>'+table(['Package','Capex Rm','Annual served bn L','Incremental NPV Rm'],[[o['option'],o['capex_zar']/1e6,f"{o['served_m3']/1e6:.2f}",f"{o['npv_zar']/1e6:.1f}"] for o in anchor['options']])
    body+='<h2>What reverses the choice?</h2>'+table(['Sensitivity','Preferred package','Improvement NPV Rm','Combined NPV Rm'],[[r['case'],r['preferred_option'],f"{r['options'][1]['npv_zar']/1e6:.1f}",f"{r['options'][2]['npv_zar']/1e6:.1f}"] for r in sensitivity])
    body+='<h2>Files and sources</h2><p>'+ ' · '.join(f'<a href="{p}">{p}</a>' for p in ['input_classification.csv','nine_worlds.csv','option_cases.csv','cashflows.csv','sensitivities.csv','results.json'])+'</p><p>'+ ' · '.join(f'<a href="{u}">Vopak source {i+1}</a>' for i,u in enumerate(data['urls']))+'</p>'
    body+='<p>Do not extrapolate group profitability to South Africa. “All other business units” combines multiple countries. The 13–17% group operating cash return ambition is not a discount rate; 5–7x and 4–8x multiples have sector-specific scope. Route capture, working capacity and project economics here remain author assumptions. Current domestic-source access, coastal capacity allocation, customer commitments, permits and engineering remain unvalidated.</p>'
    (OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Vopak illustrative investment</title><style>body{font:16px Arial;margin:35px;color:#222;max-width:1200px}h1,h2{color:#0a2373}.flag{font-weight:bold;background:#eee;padding:14px}td,th{padding:12px;border-bottom:1px solid #ddd;text-align:left}table{border-collapse:collapse;width:100%}p{line-height:1.5}</style>'+body,encoding='utf-8')
    print(json.dumps({'anchor':[{k:o[k] for k in ['option','npv_zar','incremental_ebitda_zar_year']} for o in anchor['options']],'thresholds':thresholds,'worlds':[(r['demand_world'],r['supply_world'],r['preferred_option'],r['preferred_npv_zar']) for r in worlds]},indent=2))

if __name__=='__main__':main()
