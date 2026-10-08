"""Build presentation copy and a six-step delivery log from calculated evidence."""
import csv
import hashlib
import json
from pathlib import Path
from lfm.governance import inventory

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/delivered/investment_bridge_2026_10_08'
data=json.loads((OUT/'evidence.json').read_text())
story=json.loads((ROOT/'pptx/story/sa_market_story_v21_2026_10_08.json').read_text(encoding='utf-8'))
story['slides'][0]['title']='Slow demand growth and greater import reliance set the baseline; road-to-rail shifts, EV adoption, power recovery and refinery changes could reshape the outlook'
story['slides'][2]['title']='Competition from Walvis Bay and Maputo shapes the volumes Vopak can capture; storage turnover determines the capacity required'
story['slides'][2]['note']+=' Competitiveness varies by destination; neither alternative gateway is yet established as competitive into Gauteng.'

requests=[
('DR01','P1','Baseline','National product balance','Latest complete calendar year and 2021/2022 bridge; petrol/diesel production, imports, exports, stock changes and statistical differences; units and coverage','Manish / Nigel review','Department / SARS / producers','Before baseline adoption','Reconcile definitions and source revisions; no residual labelled as production'),
('DR02','P1','Capture','Terminal movements','Latest 36 complete months; terminal, product, origin, destination, customer ID, receipt/dispatch m3; flag Durban-Lesedi transfers and final customer deliveries','Nigel to coordinate','Vopak operations / commercial','Before market-share estimate','Deduplicate chain deliveries; reconcile monthly totals to operating reports'),
('DR03','P1','Assets','Working capacity and service limits','Tank/product gross and working m3; unavailable/committed capacity; stock policy; actual turns; monthly receipt/dispatch m3; hourly and peak limits; downtime','Nigel to coordinate','Vopak operations','Before capacity-shortfall conclusion','Eligible working tankage and achievable throughput reconciled by product and terminal'),
('DR04','P1','Routes','Matched delivered economics','Same petrol/diesel spec and inland destination; dated product basis and handling/road/rail/pipeline/border/loss/finance costs; tax basis, currency, transit time, access rights and available annual capacity','Manish / Nigel review','Logistics operators / Vopak','Before corridor ranking','Compare same product/date/destination; confirm tanker access and service availability'),
('DR05','P1','Capture','Customer access and commitments','Anonymised customer/product/destination annual m3; sourcing alternatives, contract dates, committed vs contestable volumes and renewal assumptions','Nigel to coordinate','Vopak commercial','Before capturable-volume adoption','Mutually exclusive customer pools; confirmed rights and no assumed capacity-share proxy'),
('DR06','P1','Returns','Commercial terms and project options','Incremental storage/handling revenue, variable and fixed costs; tank/debottleneck capex, schedule, ramp-up, working capital, tax, hurdle rate and asset life; effects on existing revenue','Nigel to coordinate','Vopak finance / engineering / commercial','Before investment recommendation','Compare existing assets, debottleneck and expansion on incremental cash flows'),
('DR07','P2','Demand worlds','Annual demand lever calibration','Product/sector activity, transferable freight tonne-km, rail traction, EV fleet replacement, ICE efficiency; Eskom/IPP/private backup separately; generation commissioning and retirements','Manish / Nigel review','Public sources / sector specialists','Before L/M/H demand adoption','No rail/EV/efficiency double count; power balance and dispatch constrain diesel'),
('DR08','P2','Supply worlds','Annual plant output calibration','SAPREF funded timing/ramp/yields; Natref availability/utilisation; Secunda gas/MRG liquids penalty; PetroSA feedstock/restart; product-specific annual output','Manish / Nigel review','Producers / public disclosures','Before L/M/H supply adoption','Nameplate converted to output; dependencies and scenario consistency reviewed')]
fields=['id','priority','step','request','required_fields_and_period','proposed_coordinator','proposed_data_provider','expiry_trigger','acceptance_test']
if not (OUT/'data_request.csv').exists():
    with (OUT/'data_request.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields+['status','received_file','received_date']);w.writeheader()
        for r in requests:w.writerow({**dict(zip(fields,r)),'status':'Prepared; not sent','received_file':'','received_date':''})

steps=[
('1','Baseline','Partial evidence calculated','2022 petrol/diesel national and Gauteng sales matched to complete litre trade; 2021 source-balance diagnostic calculated.','Sales/consumption definitions; latest whole-market production and stock movements.','DR01','baseline.csv; historical_balance.csv','Approve a reconciled common-year product balance before M/M adoption'),
('2','Route competition','Calculation implemented; inputs open','Delivered-cost and price-headroom calculator; seven route/mode records; existing OSM connectivity retained.','Destination-specific quotes, border treatment, tanker access, service capacity and reliability.','DR04','route_readiness.csv; model/investment_bridge.py::delivered_economics','No route ranking until matched costs and access are validated'),
('3','Vopak capture','Calculation implemented; inputs open','Explicit accessible-market/capture screen capped by route capacity; transfer exclusion rules and request fields prepared.','Customer allocation, throughput and mutually exclusive customer pools.','DR02; DR05','model/investment_bridge.py::capture_screen','Publish share only with matched market boundary and unique customer deliveries'),
('4','Existing assets','Gross screen calculated; working-capacity test implemented','Existing registered 1/2/3-turn gross sensitivity reproduced; required turns and receipt/dispatch bottleneck calculator implemented.','Product-eligible working m3, achievable turns, committed capacity and peak constraints.','DR03','evidence.json::terminal_screens; model/investment_bridge.py::terminal_screen','Confirm a binding operating constraint before sizing expansion'),
('5','Investment economics','Threshold calculation implemented; inputs open','Pre-tax level break-even volume calculator handles zero hurdle and nonpositive contribution; no return figures invented.','Project capex, rates, incremental costs, life, hurdle, ramp-up, tax and working capital.','DR06','model/investment_bridge.py::break_even_screen','Full incremental cash-flow appraisal required before recommendation'),
('6','Nine worlds','Nine-cell register and balance calculation implemented','Explicit L/M/H product-balance calculator; import need and surplus separated; nine outcome rows with unfilled commercial fields.','Annual demand/output paths and route/capture/operating/finance assumptions in every cell.','DR07; DR08; DR02-06','nine_worlds.csv; model/investment_bridge.py::nine_world_balances','M/M first; dependencies and extreme combinations reviewed before scenario use')]
logpath=ROOT/'workstreams/WS0_governance/workplan/sa_investment_bridge_2026_10_08.csv'
if not logpath.exists():
    with logpath.open('w',newline='',encoding='utf-8') as f:
        fs=['step','work_package','status','implemented','remaining','request_ids','evidence','expiry_trigger','proposed_owner','reviewer','approval']
        w=csv.DictWriter(f,fieldnames=fs);w.writeheader()
        for r in steps:w.writerow({**dict(zip(fs[:8],r)),'proposed_owner':'Manish; Nigel coordinates Vopak data','reviewer':'Henry / Nigel (not yet reviewed)','approval':'Not approved for investment reliance'})

# Blank request tables are collection templates, not model defaults or assumed zeros.
templates={
 'terminal_monthly':['period','terminal','product','customer_id','origin','destination','movement_id','chain_delivery_id','movement_type','volume_m3','is_interterminal_transfer','source'],
 'terminal_capacity':['period','terminal','product','eligible_working_m3','committed_working_m3','achievable_monthly_turns','receipt_limit_annual_m3','dispatch_limit_annual_m3','peak_constraint','source'],
 'route_costs':['as_of','product','origin','destination','mode','product_zar_m3','handling_zar_m3','transport_zar_m3','border_zar_m3','losses_zar_m3','inventory_finance_zar_m3','destination_price_zar_m3','required_margin_zar_m3','available_m3_year','access_verified','tax_basis','source'],
 'investment_options':['option','capex_zar','annual_fixed_cost_zar','incremental_contribution_zar_m3','discount_rate_fraction','life_years','ramp_up','tax_basis','working_capital','source'],
 'world_paths':['year','product','demand_world','supply_world','demand_m3','domestic_output_m3','exports_m3','stock_build_m3','source']}
collection=OUT/'collection_templates';collection.mkdir(exist_ok=True)
for name,cols in templates.items():
    if not (collection/f'{name}.csv').exists():
        with (collection/f'{name}.csv').open('w',newline='',encoding='utf-8') as f:csv.writer(f).writerow(cols)

def slide(title,headers,rows,note,section=0,widths=None):
    return dict(title=title,section=section,headers=headers,rows=rows,note=note,
                column_widths=widths or [165,329,344.8],font_size=12,title_font_size=23.0)
request_slide=slide('Operating and commercial data will determine how much growth existing assets can serve',
 ['Data request','Required detail','Decision it unlocks'],[
 ['Volumes and customers\nDR02 / DR05','Monthly m³ by terminal, product, customer and destination; transfer flags; contracts and contestable volumes.','Establish unique customer deliveries, accessible demand and Vopak capture.'],
 ['Working capacity\nDR03','Product-eligible working tanks, actual turns, committed capacity, stock policy and receipt/dispatch limits.','Test higher turnover before debottlenecking or adding storage.'],
 ['Competing routes\nDR04','Matched delivered costs, transit time, access and available capacity from Durban, Maputo, Walvis Bay and domestic sources.','Identify competitive routes to the same inland customer.'],
 ['Commercial returns\nDR06','Rates, incremental costs, capex, schedule, ramp-up, working capital and return hurdle by investment option.','Establish break-even throughput and the value of each option.'],
 ['Market and plant paths\nDR01 / DR07 / DR08','Reconciled product balance; annual demand levers and plant output, including power, rail, EVs and Secunda gas/MRG.','Calibrate M/M, then test the investment across all nine worlds.']],
 'Request prepared, not sent. Proposed coordination: Nigel with Vopak operations/commercial/finance; Manish for public evidence. Monthly data: latest 36 complete months; aligned product, unit and period definitions. Detailed fields, acceptance tests and triggers: data_request.csv.',4)
story['slides'].insert(14,request_slide)
# Correct authored cross-references after the new main-story page.
for s in story['slides']:
    if 'note' in s:s['note']=s['note'].replace('appendix p26','appendix p27')
base=data['baseline'];hist=data['historical_balance_diagnostic']
baseline_slide=slide('A matched demand snapshot is available, but the domestic supply balance still needs reconciliation',
 ['Evidence / bn litres','Petrol','Diesel'],[
 ['2022 national sales',f"{base[0]['national_sales_bn_l']:.2f}",f"{base[1]['national_sales_bn_l']:.2f}"],
 ['2022 Gauteng sales',f"{base[0]['gauteng_sales_bn_l']:.2f}",f"{base[1]['gauteng_sales_bn_l']:.2f}"],
 ['2022 imports / exports',f"{base[0]['imports_bn_l']:.2f} / {base[0]['exports_bn_l']:.2f}",f"{base[1]['imports_bn_l']:.2f} / {base[1]['exports_bn_l']:.2f}"],
 ['2021 balance diagnostic',f"{hist[0]['residual_before_stat_difference_bn_l']:.2f} statistical difference needed to reconcile reported supply and final consumption.",f"{hist[1]['residual_before_stat_difference_bn_l']:.2f} statistical difference needed to reconcile reported supply and final consumption."],
 ['Decision consequence','Sales less net imports is a residual, not measured domestic output. Confirm product and stock boundaries.','Provincial sales establish demand scale, not source allocation or flows captured by Vopak.']],
 'Department sales: four quarters; SARS trade: 12 months and litre units only, blends/other units excluded. 2021 energy-balance consumption differs from sales; statistical differences are not stock changes. Source hashes and exact values: investment_bridge_2026_10_08/evidence.json.',widths=[220,309.4,309.4])
implementation_slide=slide('The six-step bridge is implemented for screening; calibration now depends on the requested inputs',
 ['Work package','Implemented now','Input needed to complete the decision'],[
 ['1 | Baseline','Matched 2022 sales/trade; 2021 balance diagnostic.','Reconcile production, stocks and source definitions.'],
 ['2 | Route competition','Delivered cost and bearable-charge calculation; route readiness register.','Matched quotes, service capacity and access.'],
 ['3 | Vopak capture','Capture calculation constrained by accessible market and route capacity.','Customer allocation and unique terminal deliveries.'],
 ['4 | Existing assets','Required-turn and operating-bottleneck calculation; gross-turn screen.','Working capacity, achievable turns and peak limits.'],
 ['5 | Investment options','Pre-tax break-even volume calculation.','Commercial inputs and full incremental cash flows.'],
 ['6 | Nine worlds','Nine-cell output register and demand/supply balance calculation.','Annual L/M/H paths; rerun routes, capture and returns.']],
 'Screening functions tested with synthetic cases; commercial outputs remain unpopulated. Not integrated into the forecast engine or independently reviewed. Owners, request IDs and expiry triggers: workstreams/WS0_governance/workplan/sa_investment_bridge_2026_10_08.csv.')
story['slides'] += [baseline_slide,implementation_slide]
story.update(main_story_pages='2–16',appendix_pages='17–33',share_inference_page=31,
             executive_summary_pages='2–5',cover_status='Data request and investment screening bridge added; scenario and commercial calibration remain open')
story['revision_22']={'user_authorisation':'Add data request page; implement and log six steps; apply agreed titles 2 and 4',
                      'added_pages':[16,32,33],'baseline_status':'Partial, not reconciled','forecast_integration':False}
(ROOT/'pptx/story/sa_market_story_v22_2026_10_08.json').write_text(json.dumps(story,indent=2,ensure_ascii=False),encoding='utf-8')

# Register only this work's new reference block. Preserve all other register entries.
reg=ROOT/'governance/assumption_register.csv'
with reg.open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f);cols=r.fieldnames;rows=list(r)
existing={r['assumption'] for r in rows}
for item in inventory():
    if item['block'].startswith('investment_bridge.') and item['assumption'] not in existing:
        row={k:item.get(k,'') for k in cols};row.update(id='LOC-'+hashlib.sha256(item['assumption'].encode()).hexdigest()[:12],review_status='unreviewed')
        rows.append(row)
with reg.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
ep=ROOT/'governance/exception_log.csv'
with ep.open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f);cols=r.fieldnames;rows=list(r)
if not any(r['id']=='EXC-INVESTMENT-BRIDGE' for r in rows):
    record={'id':'EXC-INVESTMENT-BRIDGE','assumption':'investment_bridge.*; model.investment_bridge','reason':'Partial historical balance and uncalibrated route/capture/operating/commercial inputs; screening functions not forecast-integrated.','owner':'manish.r@africaia.com','risk':'Statistical residuals may be treated as production; route connectivity or gross tankage may be treated as capturable throughput; screening thresholds may be mistaken for returns.','expiry_trigger':'Before M/M adoption, market-share publication or investment recommendation; recheck on receipt of DR01-DR08','expires_on':'2026-11-12','migration_path':'Complete data request; reconcile baseline; calibrate route/capture/working capacity; implement incremental cash flows; independently review nine worlds.','status':'open','validity':'2026'}
    rows.append({k:record.get(k,'') for k in cols})
with ep.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
print('Prepared v22 story, data request, collection templates and six-step log')
