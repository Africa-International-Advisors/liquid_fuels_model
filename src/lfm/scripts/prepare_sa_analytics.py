"""Freeze a declared evidence snapshot for the authorised October analytics."""
import csv, hashlib, json
from pathlib import Path
import yaml
from lfm.governance import inventory

ROOT = Path(__file__).resolve().parents[3]
V = ROOT / 'assumptions/2026'
def rows(name):
    with (V/name).open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))
def main():
    data = {}
    def add(key, value, unit, source, basis='Reported input'):
        data[key] = dict(value=value, unit=unit, source=source, basis=basis)
    for r in rows('timeseries/fuel_sales_department.csv'):
        if r['product'] in ('petrol','diesel') and 2013 <= int(r['period']) <= 2023:
            add('sales_'+r['product']+'_'+r['period'],float(r['value'])/1e9,'bn L','Department national fuel sales; '+r['source_file'])
    for r in rows('timeseries/fuel_sales_fiasa.csv'):
        if r['product'] in ('petrol','diesel') and r['period']=='2024':
            add('fiasa_'+r['product']+'_2024',float(r['value'])/1e9,'bn L','FIASA Annual Report 2025; definition reconciliation pending','Alternative source anchor')
    for r in rows('timeseries/energy_balance_department.csv'):
        if r['product']=='diesel' and r['flow_key'] in ('mining','industry','construction','agriculture','road') and 2018<=int(r['period'])<=2021:
            add('eb_'+r['flow_key']+'_'+r['period'],float(r['value'])/1e9,'bn L','Department energy balance '+r['period']+'; '+r['flow_key'])
    activity=rows('timeseries/activity_statssa_monthly.csv')
    for sector,series in [('mining','mining_volume_total'),('manufacturing','manufacturing_volume_total')]:
        for y in range(2018,2026):
            vals=[float(r['value']) for r in activity if r['series']==series and r['period'].startswith(str(y))]
            if len(vals)!=12: raise ValueError((sector,y,len(vals)))
            add(sector+'_activity_'+str(y),sum(vals)/12,'index 2019=100','Stats SA monthly production index; twelve-month mean')
    for r in rows('timeseries/macro_statssa.csv'):
        if r['series']=='agriculture_forestry_and_fishing' and 2018<=int(r['period'])<=2025:
            add('agriculture_activity_'+r['period'],float(r['value'])/1e9,'bn real 2015 ZAR','Stats SA P0441 agriculture real GVA')
    for r in rows('timeseries/eskom_fuel_eaf_review_2026_10_07.csv'):
        if r['series']=='eskom_ocgt_diesel_and_kerosene' and 2021<=int(r['period'])<=2025:
            add('eskom_'+r['period'],float(r['value'])/1000,'bn L','Eskom Integrated Report 2025 p141; FY ending March; diesel and kerosene','FY proxy for calendar year, fuel mix retained')
    for r in rows('timeseries/ocgt_generation_eskom.csv'):
        if r['series']=='ipp_ocgt' and 2023<=int(r['period'])<=2025:
            add('ipp_gwh_'+r['period'],float(r['value']),'GWh','Eskom statistical tables; IPP OCGT generation; FY ending March')
    for r in rows('timeseries/freight_payload_statssa_review.csv'):
        add('freight_'+r['mode']+'_'+r['period'],float(r['value'])/1000,'million tonnes','Stats SA P7162 December 2025, p7; all reported freight, not tonne-km')
    trade=rows('timeseries/fuel_trade_sars_by_office.csv')
    for y in range(2019,2026):
        for port in ('Durban','Komatipoort','All'):
            for p in ('petrol','diesel'):
                for flow in ('import','export'):
                    if port!='All' and flow=='export': continue
                    vals=[float(r['value']) for r in trade if r['period']==str(y) and r['product']==p and r['flow']==flow and r['unit']=='litres' and (port=='All' or r['district_office']==port)]
                    add(f'trade_{port}_{flow}_{p}_{y}',sum(vals)/1e9,'bn L','SARS customs by office; litres only; office is a gateway proxy')
    for r in rows('reference/refinery_output_operators.csv'):
        if r['period'] in ('2024','2025','2026'):
            plant='Astron' if r['plant'].startswith('Astron') else r['plant']
            add(f'output_{plant}_{r["period"]}',float(r['value']),r['unit'],'Operator production: '+r['source_file']+'; '+r['note'])
    payload={'evidence':data,'assumptions':{
        'petrol_activity_growth':0.005,'petrol_efficiency_change':0.015,
        'nonpower_diesel_growth':0.01,'road_diesel_efficiency_change':0.005,
        'petrol_road_share':0.97,'road_diesel_freight_share':0.75,
        'ipp_litres_per_kwh':0.31,'eskom_diesel_share':1.0,
        'private_power_2023':0.8,'private_power_2024':0.6,'private_power_2025':0.2,
        'barrel_litres':158.987294928,'btu_mj':0.00105505585262,
        'secunda_pd_share':0.9,'secunda_petrol_share_of_pd':0.65,
        'natref_share':0.6364,'natref_petrol_yield':0.305,'natref_diesel_yield':0.34,
        'astron_pd_share':0.8,'astron_petrol_share_of_pd':0.5,'astron_mj_per_litre':35.5,
        'road_distance_durban_km':600,'road_distance_matola_km':550,
        'truck_cost_zar_km':25,'truck_payload_litres':40000,
        'terminal_cost_durban_zar_l':0.2,'terminal_cost_matola_zar_l':0.25,
        'border_cost_matola_zar_l':0.1,'border_delay_days':1,'truck_delay_zar_day':4000,
        'inventory_price_zar_l':15,'financing_rate':0.12,
        'matola_landed_premium_zar_l':0,'galp_working_fraction':0.85,
        'galp_monthly_turns':1.5,'galp_sa_allocation':0.2,
        'petromoc_pd_fraction':0.75,'petromoc_working_fraction':0.8,
        'petromoc_monthly_turns':1,'petromoc_sa_allocation':0.1,
        'operating_days':330,'border_delay_low_days':0,'border_delay_high_days':3,
        'sapref_bpd':180000,'petrosa_bpd':45000,'restart_pd_yield':0.7,
        'unreported_construction_bn':0,
    },'scenarios':{
        'Low imports':{'activity_growth':0.005,'efficiency':0.015,'rail_shift':0.15,'rail_diesel_rebound':0.1,'power_retained':0.35,'supply_multiplier':1.15,'sapref_start':2029,'sapref_utilisation':0.65,'petrosa_start':2029,'petrosa_utilisation':0.5,'moz_diversion_bn':0.6},
        'Base':{'activity_growth':0.015,'efficiency':0.01,'rail_shift':0.075,'rail_diesel_rebound':0.1,'power_retained':0.5,'supply_multiplier':1.0,'sapref_start':2099,'sapref_utilisation':0,'petrosa_start':2099,'petrosa_utilisation':0,'moz_diversion_bn':0.2},
        'High imports':{'activity_growth':0.025,'efficiency':0.005,'rail_shift':0.025,'rail_diesel_rebound':0.1,'power_retained':1.0,'supply_multiplier':0.85,'sapref_start':2099,'sapref_utilisation':0,'petrosa_start':2099,'petrosa_utilisation':0,'moz_diversion_bn':0.05}
    },'nodes':[
        ['Galp/IPG Matola',60000,'petrol + diesel m3','Operating; inaugurated 3 December 2020','https://www.galp.com/corp/pt/media/comunicados-de-imprensa/comunicado/id/1172'],
        ['Petromoc Lingamo',390000,'all liquid fuels m3','Operating; includes jet and paraffin; capacity overlap with other operators unconfirmed','https://www.petromoc.co.mz/product-service/logistica/'],
        ['Petromoc Nacala',47500,'all liquid fuels m3','Northern regional supply; no incremental SA allocation assumed','https://www.petromoc.co.mz/product-service/logistica/'],
        ['Petromoc Pemba',18000,'all liquid fuels m3','Northern regional supply; no incremental SA allocation assumed','https://www.petromoc.co.mz/product-service/logistica/'],
        ['Galp/IPG Beira',None,'capacity not established here','Operating since February 2021; central regional supply','https://www.galp.com/mz/pt-pt/institucional/logistica'],
        ['Temane PSA',4000,'barrels light oil/day','Production began December 2025; light oil, gas and LPG, not finished petrol/diesel','https://sasol.com/our-businesses/energy/gas-sourcing-and-operations'],
        ['CFM Matola berth',5000000,'tonnes/year all petroleum','Shared berth capacity; not additive to storage or SA throughput','https://www.cfm.co.mz/terminal-de-combustiveis/']
    ]}
    config={'snapshot':dict(value=payload,units='Per-key units: bn litres unless explicitly stated; fractions; years; ZAR; km',source='Authorised analytical assumptions 11 October 2026. Evidence provenance retained per item. Demand: 2023 Department anchor; 2024 FIASA sensitivity. Sector intensity: average 2018-2021. FY power proxies calendar years, all Eskom fuel provisionally allocated to diesel. Private backup assumptions replace part of the residual and are not measured. Supply: FY2025 proxy, product-yield assumptions, no restart base case. Route rates/distances and allocation are illustrative, not quotes. Scenarios are sensitivities, not probabilities.',last_updated='2026-10-11',owner='nigel.zhuwaki',confidence='unassessed',provisional=True,register_id='REG-SA-ANALYTICS-202510',exception_id='EXC-SA-ANALYTICS-202510')}
    target=V/'sa_analytics_2025.yaml'
    if target.exists(): raise FileExistsError(target)
    target.write_text(yaml.safe_dump(config,sort_keys=False,allow_unicode=True),encoding='utf8')
    ep=ROOT/'governance/exception_log.csv'
    with ep.open(encoding='utf-8-sig',newline='') as f: er=list(csv.DictReader(f))
    er.append(dict(id='EXC-SA-ANALYTICS-202510',assumption='sa_analytics_2025.snapshot',reason='Estimated segment allocation, FY/calendar proxy, yields, demand-supply residual and route economics require review.',temporary_value='See declared snapshot and delivered workbook',owner='nigel.zhuwaki',approver='',risk='Levels and import requirement depend materially on source scopes and analyst assumptions.',expiry_trigger='Before external presentation or investment approval',expires_on='2026-11-12',migration_path='Manish reconcile sales/trade and plant scope; Nigel obtain route quotes/customer access and approve assumptions; replace estimates with reported inputs.',status='open',validity='2026'))
    with ep.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(er[0]));w.writeheader();w.writerows(er)
    rp=ROOT/'governance/assumption_register.csv'
    with rp.open(encoding='utf-8-sig',newline='') as f: reg=list(csv.DictReader(f))
    for r in inventory():
        if r['block']!='sa_analytics_2025.snapshot': continue
        reg.append({k:('LOC-'+hashlib.sha1(r['assumption'].encode()).hexdigest()[:12] if k=='id' else 'unreviewed' if k=='review_status' else r.get(k,'')) for k in reg[0]})
    with rp.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(reg[0]));w.writeheader();w.writerows(reg)
    print('Frozen snapshot and registered',len(data),'evidence inputs')
if __name__=='__main__': main()
