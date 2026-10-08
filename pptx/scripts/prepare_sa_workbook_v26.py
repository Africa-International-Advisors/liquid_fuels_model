"""Prepare presentation evidence and page specifications from Manish's workbook.

Reads a locally recalculated review copy. Does not change engine inputs or forecasts.
"""
from pathlib import Path
import csv
import hashlib
import json
import openpyxl

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / 'runs/review/manish_workbook_2026_10_08_latest'
OUT = ROOT / 'pptx/story'
source = json.loads((REVIEW / 'source.json').read_text())
wb_path = REVIEW / 'Demand_baseline_workshop_2026_10_08_history_recalculated.xlsx'
wb = openpyxl.load_workbook(wb_path, data_only=True)
original = openpyxl.load_workbook(REVIEW / 'Demand_baseline_workshop_2026_10_08_history.xlsx', data_only=False)
errors = [(s.title, c.coordinate, c.value) for s in wb for row in s for c in row if c.data_type == 'e']
assert not errors, errors
evidence = []


def value(sheet, cell):
    c = wb[sheet][cell]
    if c.value is None:
        raise ValueError(f'Missing evidence: {sheet}!{cell}')
    raw = original[sheet][cell].value
    if not any(x['sheet'] == sheet and x['cell'] == cell for x in evidence):
        evidence.append({'sheet': sheet, 'cell': cell, 'value': c.value,
                         'formula': raw if isinstance(raw, str) and raw.startswith('=') else None})
    return c.value


def bn(sheet, cell):
    return f'{value(sheet, cell) / 1000:.2f}'


story = json.loads((OUT / 'sa_market_story_v25_2026_10_08.json').read_text(encoding='utf-8'))
old = story['slides']
for page, spec in enumerate(old, 2):
    spec['source_page'] = page
    spec['revision_action'] = 'retained'
    spec['audit_reason'] = 'Reviewed against workbook scope; existing evidence or illustrative treatment retained.'


def update(page, reason, **fields):
    spec = old[page - 2]
    spec.update(fields)
    spec['revision_action'] = 'updated'
    spec['audit_reason'] = reason


sales23 = value('History', 'Q71') / 1000
sales24 = value('History', 'R71') / 1000
bev25 = value('Vehicle history', 'S31')
phev25 = value('Vehicle history', 'S33')
hev25 = value('Vehicle history', 'S35')
bevshare = value('Vehicle history', 'S32')
assert wb['History']['A84'].value == 'Gauteng petrol, estimated'
assert wb['History']['A104'].value == 'Gauteng diesel, estimated'
gauteng23 = (value('History', 'Q84') + value('History', 'Q104')) / 1000
gauteng24 = (value('History', 'R84') + value('History', 'R104')) / 1000

rows = [list(r) for r in old[0]['rows']]
rows[0][1] = f'2023 Department sales: {sales23:.2f}bn L.\nPetrol CAGR -2.08%; diesel +0.82%.\nOwn Eskom fuel fell 40% in FY2025.'
rows[0][2] = 'Sector activity, fleet replacement and\npower dispatch change fuel use.\n2024 sales remain unverified.'
update(2, 'Add latest comparable national scale and sales-source qualification.', rows=rows,
       note='Department sales 2013-2023; 2023 total 21.94bn L. FIASA 2024 total 20.76bn L is unverified; no 2025 sales. SARS imports 2020-2025. Eskom FY2025 own diesel + kerosene. M/M remains an uncalibrated reference.')
update(6, 'Keep comparable 2013-2023 chart; add latest-year coverage and reconciliation caution.',
       takeaway=f'2023 Department sales total {sales23:.2f}bn L. The 2024 FIASA comparison is {sales24:.2f}bn L, unverified; no 2025 sales figure is available.',
       note='Department sales 2013-2023: petrol CAGR -2.08%, diesel +0.82%. FIASA 2024 is excluded from the trend. Workbook History Q71/R71. RAF levy evidence uses fiscal years and still needs reconciliation.')
rows = [list(r) for r in old[5]['rows']]
rows[1][2] = 'Road carries 85.3% of tonnes.\nWorkbook truck-fuel proxy: 3.15bn L\nin 2023, partial operator coverage.'
rows[2][2] = 'Activity differs by sector.\n2024 indicative diesel: mining 1.40,\nindustry residual 0.17, farms 0.96bn L.'
update(7, 'Add sector fuel scale and the freight-operator proxy without changing measured support bars.', rows=rows,
       note=old[5]['note'] + ' Workbook Sector history: post-2021 litres estimated. Freight proxy = survey fuel spending / wholesale price; partial coverage.')
update(8, 'Show gross versus net imports and preserve sales/production boundaries.',
       takeaway=f'2025 gross imports: diesel {bn("History", "S36")}bn L and petrol {bn("History", "S37")}bn L. Combined net imports: {bn("History", "S44")}bn L; port allocation and Vopak capture remain open.')
rows = [list(r) for r in old[8]['rows']]
rows[1][1] = '140,000 m3 clean-product capacity.\nIncludes the 40,000 m3 expansion\ncommissioned in October 2025.'
update(10, 'Clarify that the commissioned Lesedi expansion is included in the existing footprint.', rows=rows)
update(11, 'Separate observed drivetrain sales from assumed efficiency and adoption paths.',
       takeaway=f'2025 sales: {bev25:,} BEVs ({bevshare:.2f}% of all new sales), {phev25:,} plug-in hybrids and {hev25:,} conventional hybrids. Each has a different fuel effect.',
       note='Stats SA freight; naamsa all-market sales 2019-2025, Workbook Vehicle history S31:S36. BEV/PHEV/HEV sales are distinct from fleet shares. Efficiency paths remain model assumptions, with OEM history and annual calibration open.')
update(12, 'Distinguish own reported burn from combined generation-derived estimates and proposed cases.',
       takeaway='Own Eskom fuel is reported separately. The workbook adds Eskom/IPP generation and four diesel stations; litres derived from output and future dispatch remain estimates.',
       note='Eskom FY ending March: reported own diesel + kerosene; Eskom/IPP GWh include kerosene output. Workbook Power fleet separates the four diesel stations. Gas switch, coal-site repowering and L/M/H settings await Nigel/Henry review.')
update(16, 'Replace the request summary with all active baseline, route, demand, supply and client gaps.',
       headers=['Outstanding request / coordinator', 'Required data / handback', 'Decision supported'],
       rows=[
           ['DR01 | Manish; Nigel review', 'Product/year sales, gross imports, exports, actual production and stocks. Resolve 2024 source; 2025 sales are absent.', 'Reconciled current market scale.'],
           ['DR04 | Manish; Nigel review', 'Port/pipeline capacity, route access and destination-matched delivered economics.', 'Accessible Durban and Lesedi markets.'],
           ['DR07/08 | Manish; Nigel/Henry review', 'Reported Eskom litres, fleet/efficiency, IPP timing and all refineries including PetroSA/Mossgas.', 'Demand and domestic-output paths.'],
           ['DR02/05 | Nigel coordinates', '36 months of site/product movements, shared transfers, destinations, customer commitments and contracts.', 'Actual market share and achievable capture.'],
           ['DR03 | Nigel coordinates', 'Working/committed tankage, turns, occupancy, downtime and receipt/dispatch limits.', 'Operating headroom and bottlenecks.'],
           ['DR06 | Nigel coordinates', 'Storage/handling terms, costs, capex, timing, tax, working capital and hurdle rate.', 'Incremental returns and investment scope.']],
       font_size=12, body_height=314, header_height=28,
       note='DR01-DR09 register and 8 October PS handback. Prepared, not sent; receipt not recorded. DR09 EV adjacency remains separate. Public estimates can proceed while client data is pending.')
rows = [list(r) for r in old[16]['rows']]
rows[0][1] = 'Workbook sector history, vehicle stock/sales, diesel-use estimates, freight and power fleet.'
rows[0][2] = 'Observed history and labelled estimates inform D1-D5; annual L/M/H paths still require agreement.'
update(18, 'Refresh evidence navigation to include the added workbook exhibits.', rows=rows)
update(19, 'Link aggregate GDP chart to the sector intensity exhibit rather than assume uniform fuel elasticity.',
       takeaway='The workbook separates mining/manufacturing indices and agricultural GVA from fuel intensity. Post-2021 sector litres are estimates; GDP alone cannot explain fuel demand.')
update(21, 'Quantify sector and jet context from the workbook while preserving sector definitions.',
       rows=[
           ['Mining', f'2024 production index {value("Sector history", "R7"):.1f}; indicative diesel {bn("Sector history", "R9")}bn L.', 'Use activity and intensity separately; balance intensity varies materially.'],
           ['Manufacturing', f'2024 output index {value("Sector history", "R17"):.1f}; indicative industry residual {bn("Sector history", "R19")}bn L.', 'Industry less mining/construction. This is not a complete industrial diesel census.'],
           ['Agriculture', f'2025 real GVA R{value("Sector history", "S23"):.1f}bn (2015 prices); indicative diesel {bn("Sector history", "S25")}bn L.', 'Fuel estimate holds 2018-2021 intensity; crop and irrigation exposure remain open.'],
           ['Aviation', f'2024 jet sales {bn("History", "R117")}bn L; {value("History", "R124"):,} ACSA movements; {value("History", "R125"):,.0f} L/movement.', 'FIASA sales unverified; movements omit non-ACSA airports. Fuel mix and routes are not separated.']],
       note='Workbook Sector history R7/R9/R17/R19/S23/S25 and History R117/R124/R125. Sector litres after 2021 are estimates; jet 2024 uses unverified FIASA. Index base 2019=100; GVA in 2015 prices.')
update(23, 'Add observed apparent replacement and distinguish cohort assumptions from efficiency history.',
       rows=[
           ['Fleet growth', f'2025 cars {value("Vehicle history", "S6")/1e6:.2f}m; LCVs {value("Vehicle history", "S7")/1e6:.2f}m; trucks {value("Vehicle history", "S8")/1e6:.3f}m.', 'Registered stock shows scale; fuel within class and opening cohort age remain unknown.'],
           ['Replacement', f'2025 apparent retirement: cars {value("Vehicle history", "S24"):.2f}%, LCVs {value("Vehicle history", "S26"):.2f}%. Model settings: 4% and 5%.', 'Stock plus sales less next stock is a diagnostic, including deregistration, exports and classification effects.'],
           ['Efficiency / EVs', 'Study mileage/fuel-use benchmarks and separate BEV, PHEV and hybrid sales are available.', 'Recent OEM efficiency history remains open. Apply gains to new cohorts and count EV transitions once.']],
       note='Workbook Vehicle history S6:S8/S24/S26. Apparent retirements are not verified scrappage. Stone et al. study uses a 2014 base; no recent OEM efficiency history or fuel-by-class stock is established.')
update(24, 'Retain comparable own-fleet reported fuel; qualify scope relative to the new fleet page.',
       takeaway='Reported own-fleet fuel fell from 1,129.5 to 679.1m L as EAF improved. Eskom/IPP output and generation-derived litres are a broader, separate series.',
       note='Eskom Integrated Report 2025, FY March, own diesel + kerosene. Workbook combined generation includes IPPs and kerosene stations; multiplying it by 0.31 L/kWh is an estimate, not reported diesel burn. Private backup remains unmeasured.')
update(25, 'Add the spending-based operator fuel proxy; preserve the tonne-kilometre evidence gap.',
       takeaway=f'2023 freight-operator fuel purchases imply ~{bn("Diesel by use", "Q28")}bn L at list diesel prices. Partial coverage and the estimated vehicle split do not establish corridor tonne-km.',
       note='Stats SA payload and transport-industry fuel purchases. Workbook Diesel by use Q28: spending / average diesel price, hire-and-reward firms only; may include petrol/lubricants. Road residual includes unseparated uses; tonne-km and rail traction remain open.')
update(27, 'Add estimated provincial updates without converting sales or capacity into current share.',
       takeaway=f'Gauteng sales: 6.81bn L observed in 2022; {gauteng23:.2f}bn estimated in 2023 and {gauteng24:.2f}bn in 2024. Customer catchment and actual Lesedi capture remain unverified.',
       note='Department provincial sales through 2022; workbook History Q84/Q104 and R84/R104 estimate later volumes. 2024 also uses unverified FIASA national sales. The chart retains observed 2013-2022 sales history, not current market share.')
rows = [list(r) for r in old[26]['rows']]
rows[0][2] = '29 proposed levers (20 original, nine added). 2030/2035 values need review; no agreed annual path yet.'
rows[1][2] = 'Output, yields and feedstock dependencies remain open. Reconcile proposed capacity, utilisation and gas assumptions.'
update(28, 'Expose the expanded lever register without adopting analyst proposals.', rows=rows,
       note='Workbook HML response has 29 levers. Examples: BEV adoption, rail diversion, mileage, prices, hybrids, truck/LCV electrification and neighbouring exports. All replacement ranges remain proposals; no forecast inputs are adopted in this pack.')
update(29, 'Replace generic fleet-data gap wording with the assembled fleet and remaining dispatch dependencies.',
       rows=[
           ['Recovery history', 'Own Eskom fuel/EAF and Eskom/IPP GWh are assembled; generation-based litres are estimated.', 'Match financial and calendar periods. Obtain reported litres and private-backup evidence.'],
           ['Fleet and retirements', 'Four diesel stations: 3,089 MW. Avon/Dedisa PPA endings and coal retirement dates are assembled.', 'Contract end is not confirmed shutdown. Siting, renewal and actual coal decisions remain open.'],
           ['Replacement / gas', 'Ankerlig/Gourikwa gas switch and coal-site turbines are case dependencies, not committed outcomes.', 'Wind/solar/gas commissioning, fuel availability and dependable output constrain peaking dispatch.'],
           ['Proposed L/M/H cases', '2030 power diesel: 86 / 637 / 4,224m L in the workbook scenarios.', 'Nigel/Henry review D22: conversion rate, backup share, load factors, repowering location and gas supply.']],
       note='Workbook Power fleet F11:S15 and N63:N65; proposed scenarios, not forecasts. Generation includes kerosene. IPP renewal, gas availability and coal-site repowering are not established. Historical burn must match scope and period.')
update(30, 'Add operator output context and reinforce product-output versus nameplate distinction.',
       rows=[
           ['S1 SAPREF', 'High capacity illustration adds 400 kbpd from assumed 2033 availability.', 'Preserve the hypothetical case; actual funding, schedule, ramp-up and product yields need evidence.'],
           ['S3 Natref', '108 kbpd remains in Medium/High; excluded in the Low 2036 stress case.', 'Availability stress only. No closure decision or date is established.'],
           ['S2 Secunda', f'Operator all-products output: {value("History", "R53"):.1f}m barrels in FY2024 and {value("History", "S53"):.1f}m in FY2025.', 'June fiscal years; product mix differs. Gas/MRG affects liquid output; do not equate barrels with diesel litres.'],
           ['S4 PetroSA', 'No restart addition in the existing capacity illustration; workbook identifies the source gap.', 'Complete the Mossgas/PetroSA feedstock, funded scope, timing and yield evidence.']],
       note='Existing capacity illustrations retained. Workbook History R53/S53: Sasol all-refined-products output, June FY. Department product production stops at 2021; stocks, plant yields and restart calibration remain open.')
update(31, 'Explain the accessible-market method alongside existing footprint proxies.',
       rows=[
           ['Durban', '45.1% of two operators\' published gross Durban tankage.', 'Incomplete, mixed-product capacity denominator. Estimate feasible product/customer flows before calculating throughput share.'],
           ['Gauteng / Lesedi', f'2022 sales 6.81bn L; workbook estimates {gauteng23:.2f}bn in 2023 and {gauteng24:.2f}bn in 2024.', 'Provincial sales are a demand proxy. Lesedi catchment, eligible products and actual deliveries remain unverified.'],
           ['Investment implication', 'Accessible market less current capture gives headroom; achievable additional capture must be tested.', 'Track shared Durban-Lesedi flows once. Compare customer volumes with working capacity, turns and dispatch limits.']],
       note='Existing capacity-scale ratios retained, not throughput shares. Workbook provincial estimates: 2023 estimated shares; 2024 estimated shares plus unverified national sales. Client throughput and commercial access remain open.')
update(32, 'Extend national evidence, add RAF reconciliation flag and retain production/stock gap.',
       rows=[
           ['2023 Department sales', bn('History','Q59'), bn('History','Q64')],
           ['2024 FIASA sales, unverified', bn('History','R59'), bn('History','R64')],
           ['2025 SARS imports / exports', f'{bn("History","S37")} / {bn("History","S40")}', f'{bn("History","S36")} / {bn("History","S39")}'],
           ['2025 sales / product output', 'Sales absent; product production series ends 2021.', 'Sales absent; product production series ends 2021.'],
           ['RAF levy cross-check', f'Combined levied volume {bn("History","R70")}bn L, year to March 2025.', 'Fiscal/accrual versus calendar sales. Reconcile coverage before interpreting the difference.'],
           ['Decision consequence', 'Sales less net imports remains a residual.', 'Stocks and definitions remain unresolved.']],
       font_size=12, body_height=314, header_height=28,
       note='Workbook History Q59/Q64/R59/R64/S36:S40/R70. RAF-derived 24.42bn L is combined fuel, fiscal/accrual basis, not an adopted calendar sales total. Product output after 2021 and stocks remain missing; 2025 trade is not 2025 consumption.')
rows = [list(r) for r in old[31]['rows']]
rows[0][1] = 'Workbook sales/trade, sector, vehicle and power history plus labelled estimates are assembled.'
rows[0][2] = 'Agree baseline year/source; reconcile production, stocks, scopes and fiscal/calendar periods.'
rows[5][2] = '29 proposed levers and fleet cases inform review. Agree annual paths before rerunning routes, capture and returns.'
update(33, 'Refresh implementation status for the analyst workbook, without asserting forecast integration.', rows=rows)
rows = [list(r) for r in old[32]['rows']]
rows[0][1] = '2023 petrol/diesel sales total 21.94bn L; sector activity and fleet evidence explain different fuel exposures.'
update(34, 'Align original synthesis with the updated consumption scale.', rows=rows)
rows = [list(r) for r in old[34]['rows']]
rows[0][2] = 'Full physical capacity for operations. The commissioned 40,000 m3 Lesedi expansion is included in 140,000 m3.'
update(36, 'Prevent double-counting the commissioned Lesedi expansion in the asset evidence.', rows=rows)

sector = {
    'title':'Mining, manufacturing and agriculture link diesel demand to sector activity',
    'section':1, 'new_key':'sectors', 'revision_action':'new', 'kind':'table',
    'headers':['Sector','2019 diesel\nbn litres','2021 diesel\nbn litres','2024 estimate\nbn litres','Activity and interpretation'],
    'column_widths':[145,110,110,130,343.8], 'font_size':12.5, 'header_height':38,'body_height':265,
    'rows':[
        ['Mining',bn('Sector history','M6'),bn('Sector history','O6'),bn('Sector history','R9'),f'2024 production index {value("Sector history","R7"):.1f} (2019=100). Fuel intensity varies materially; mine and on-road use overlap.'],
        ['Manufacturing / non-specified industry',bn('Sector history','M16'),bn('Sector history','O16'),bn('Sector history','R19'),f'2024 output index {value("Sector history","R17"):.1f}. Fuel is industry less mining/construction, not all industrial use.'],
        ['Agriculture / forestry',bn('Sector history','M22'),bn('Sector history','O22'),bn('Sector history','R25'),f'2024 GVA R{value("Sector history","R23"):.1f}bn, 2015 prices. Weather, crop cycles, irrigation and transport affect exposure.']],
    'takeaway':'Post-2021 fuel estimates hold 2018-2021 average intensity. Mining/manufacturing use litres per index point; agriculture uses litres per real rand of activity.',
    'note':'Workbook Sector history M6/O6/R9, M16/O16/R19, M22/O22/R25. Department energy balance to 2021; later fuel estimated with activity and average intensity. Sector attribution and road overlap require review.',
    'audit_reason':'New requested sector exhibit; separate observed fuel history from activity-based estimates.'}
vehicle = {
    'title':'Vehicle stock and sales expose fuel-demand calibration gaps',
    'section':3, 'new_key':'vehicles', 'revision_action':'new','kind':'table',
    'headers':['Calibration item','Observed evidence','Model / calibration reference','Implication / limitation'],
    'column_widths':[145,235,140,318.8],'font_size':12,'header_height':28,'body_height':300,
    'rows':[
        ['2025 registered fleet',f'Cars {value("Vehicle history","S6")/1e6:.2f}m; LCVs {value("Vehicle history","S7")/1e6:.2f}m; trucks {value("Vehicle history","S8")/1e6:.3f}m.','Opening cohorts need review.','Age and fuel within class are missing; all-class fuel counts are available only for December 2023.'],
        ['New-sales mix, 2025',f'Cars {value("Vehicle history","S18"):.1f}%; LCVs {value("Vehicle history","S19"):.1f}%; medium/heavy {value("Vehicle history","S20"):.1f}%.','78% / 18% / 4%.','Observed class mix differs. Agree segmentation before adopting a replacement.'],
        ['Apparent retirement, 2025',f'Cars {value("Vehicle history","S24"):.2f}%; LCVs {value("Vehicle history","S26"):.2f}%.','4% cars; 5% LCVs.','Derived from stock and new sales; includes classification changes, exports and deregistrations.'],
        ['New drivetrains, 2025',f'BEV {bev25:,}; PHEV {phev25:,}; conventional hybrid {hev25:,}.',f'BEV observed share {bevshare:.2f}%.','All new-sales denominator. Fleet share, charging behaviour and hybrid fuel savings differ.'],
        ['Petrol-use diagnostic, 2023',f'{value("Vehicle history","Q52"):,.0f} L per registered petrol vehicle.','Passenger setting implies 1,615 L/year.','Aggregate versus passenger scope differs. Investigate mileage and fuel-use calibration, not a direct replacement.']],
    'note':'Workbook Vehicle history S6:S8/S18:S20/S24/S26/S31:S36/Q52. NaTIS and naamsa classes are not identical. Apparent retirement is not verified scrappage; petrol diagnostic compares different scopes.',
    'audit_reason':'New requested fleet and model-calibration evidence, with scope limits retained.'}
power = {
    'title':'The diesel fleet and replacement timing define the power-demand cases',
    'section':3, 'new_key':'power_fleet','revision_action':'new','kind':'power',
    'fleet_headers':['Diesel station','MW','Owner'],
    'fleet_rows':[[value('Power fleet',f'A{r}').split(' (')[0],f'{value("Power fleet",f"F{r}"):,.0f}', 'Eskom' if r<13 else 'Independent'] for r in [11,12,13,14]],
    'case_headers':['Proposed case','2030 m L','2035 m L','Key dependency'],
    'case_rows':[
        ['Low',f'{value("Power fleet","N63"):,.0f}',f'{value("Power fleet","S63"):,.0f}','Gas switch; PPAs end; no coal-site turbines.'],
        ['Medium',f'{value("Power fleet","N64"):,.0f}',f'{value("Power fleet","S64"):,.0f}','3 GW at coal sites; gas available; diesel backup.'],
        ['High',f'{value("Power fleet","N65"):,.0f}',f'{value("Power fleet","S65"):,.0f}','6 GW at coal sites; no gas; diesel peakers.']],
    'timeline':'Avon / Dedisa PPAs end in 2031 / 2030.\nFive coal sites have exemptions to March 2030; final outcomes remain open.\nGas-switch and turbine locations are assumptions, not committed projects.',
    'note':'Workbook Power fleet F11:F15, N63:N65 and S63:S65. Proposed cases, Nigel/Henry review D22. 0.31 L/kWh, backup fraction, load factors, gas supply and coal-site repowering need review. Kerosene stations and private backup are separate.',
    'audit_reason':'New fleet inventory and analyst power scenarios, expressly unapproved.'}
tree = {
    'title':'Durban and Lesedi market sizing and investment issue tree',
    'section':3,'new_key':'issue_tree','revision_action':'new','kind':'import',
    'note':'8 October PS framework; workbook History Q71/R71. 2023 Department sales 21.94bn L; 2024 FIASA 20.76bn L, unverified. Estimate accessible markets, then verify actual capture. Shared flows and client operating/economic inputs remain open.',
    'audit_reason':'Integrate the approved issue tree into Resolution with updated baseline evidence.'}
final = []
for page, spec in enumerate(old,2):
    final.append(spec)
    if page==7: final.append(sector)
    if page==14: final.append(tree)
    if page==23: final.append(vehicle)
    if page==29: final.append(power)
story['slides'] = final
# Only internal deck references move; external report page citations stay intact.
for page, replacements in {
    4: {'pp35–38': 'pp39–42'},
    5: {'Inputs: p37; downside: p38': 'Inputs: p41; downside: p42'},
    10: {'request: p16': 'request: p18', 'moved to p39': 'moved to p43'},
    15: {'illustratively on p35': 'illustratively on p39'},
}.items():
    spec=next(s for s in final if s.get('source_page')==page)
    for before, after in replacements.items():
        assert before in spec['note'], (page, before)
        spec['note']=spec['note'].replace(before,after)
    if spec['revision_action']=='retained':
        spec['revision_action']='references'
        spec['audit_reason']='Internal page references updated; evidence and illustrative calculations retained.'
story['revision_26'] = {'source':source,'recalculated_sha256':hashlib.sha256(wb_path.read_bytes()).hexdigest(),
                        'status':'Evidence update; model assumptions and illustrative investment economics unchanged',
                        'new_pages':[i+2 for i,s in enumerate(final) if s['revision_action']=='new'],
                        'formula_errors':0,'forecast_integration':False,
                        'source_disagreements':['HML response jet baseline says 4,090 L/movement; History R125 recalculates to about 4,285. Use History for historical evidence, leave proposal unadopted.',
                                                'Reported own Eskom fuel and Eskom/IPP generation-derived litres have different scope and periods.',
                                                'Industry model replacement proposal and the manufacturing energy-balance residual have different sector boundaries.']}
for spec in final:
    if spec['revision_action'] in ('updated','new'):
        spec['analysis_detail'] = spec.get('analysis_detail','') + '\nWorkbook source commit: ' + source['commit'] + '\n' + spec['audit_reason']
(OUT/'sa_market_story_v26_2026_10_08.json').write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'sa_workbook_evidence_v26_2026_10_08.json').write_text(json.dumps({'source':source,'cells':evidence,'disagreements':story['revision_26']['source_disagreements']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
audit_path = ROOT/'workstreams/WS3_reporting_delivery/sa_pack_workbook_audit_2026_10_08.csv'
with audit_path.open('w',newline='',encoding='utf-8') as stream:
    writer=csv.DictWriter(stream,fieldnames=['v26_page','v25_page','title','action','reason','source_commit'])
    writer.writeheader()
    writer.writerow({'v26_page':1,'v25_page':1,'title':story['cover_title'].replace('\n',' '),'action':'retained','reason':'Cover and source branding retained.','source_commit':source['commit']})
    for i,spec in enumerate(final,2):
        writer.writerow({'v26_page':i,'v25_page':spec.get('source_page',''),'title':spec['title'],'action':spec['revision_action'],'reason':spec['audit_reason'],'source_commit':source['commit']})
print(f'Prepared {len(final)+1} pages; {len(evidence)} cited workbook cells; four new exhibits.')
