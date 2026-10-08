"""Make investment conditions and nine-world choices explicit; no new forecasts."""
from copy import deepcopy
import csv,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
story=json.loads((ROOT/'pptx/story/sa_market_story_v22_2026_10_08.json').read_text(encoding='utf-8'))
def page(n):return story['slides'][n-2]
scr=deepcopy(page(4));scr['section']=0
scr['title']='Demand, supply and corridor access translate into captured throughput and required tank turns'
story['slides'].append(scr)

page(3).update(title='Prioritise capture and turnover through existing assets; expand where profitable demand exceeds achievable capacity',
 headers=['Working recommendation','Investment logic','Condition for commitment'],rows=[
 ['Capture inland\nsupply','Win accessible customer flows from imported and domestic sources.','Prove delivered competitiveness and sufficient customer volume.'],
 ['Use existing\nassets first','Increase turnover where tanks and receipt/dispatch allow.','Confirm working capacity and the actual operating constraint.'],
 ['Stage corridor\nand capacity spend','Compare access improvements, rail loading, debottlenecking and new tanks.','Fund the least-cost viable option that removes the proven constraint.'],
 ['Keep strategic\noptions open','Test all nine worlds and emerging gateways; screen EV adjacencies separately.','Apply p4 to fuel-capacity expansion; assess operational and EV options on their own economics.']],
 note='Working recommendation, not an approved investment. Four numeric decision tests follow on p4; nine-world investment priorities on p5. Customer, operating and commercial inputs remain open.')

e=json.loads((ROOT/'output/delivered/investment_bridge_2026_10_08/evidence.json').read_text())
dur,les=[x['gross_monthly_turns_per_bn_litres'] for x in e['terminal_screens']]
page(4).update(title='Expand fuel-logistics capacity only when four investment tests pass',
 headers=['Decision test','Numeric condition','What we know now','Investment consequence'],
 column_widths=[140,215,250,233.8],icons=['transport','corridor','supply','investment'],
 icon_dir='output/delivered/sa_scr_icons_2026_10_08',rows=[
 ['Customer\nvolume','Secured incremental m³/year ≥ break-even m³/year.','Volume threshold: pending customer commitments, rates and project costs.','Size and phase the option to the volume that can actually be won.'],
 ['Route\neconomics','Delivered-cost headroom ≥ R0/m³ after the required margin.','Headroom: pending matched quotes for the same product and destination.','Include emerging Maputo and Walvis Bay routes and domestic alternatives.'],
 ['Capacity\nconstraint','Captured m³/year − achievable m³/year > 0.','Actual shortfall: unknown. Each 1bn L/year equals '+f'{dur:.2f} Durban / {les:.2f} Lesedi gross monthly turns.','Improve access or dispatch first where they bind; add tanks only if storage binds.'],
 ['Incremental\nreturn','NPV > R0 at the agreed hurdle rate.','NPV and hurdle: pending finance inputs. Test ramp-up and downside volumes.','Select a viable option and stage commitment against contracts and delivery.']],
 note='Decision rules for fuel-capacity expansion, not measured results. Gross turns indicate scale, not achievable working capacity; Durban includes mixed products. Full NPV requires project cash flows. Cost-saving improvements need their own incremental-return test; EV investment is assessed separately. SCR synthesis: p34.')

page(5).update(title='Nine worlds identify investment priorities; capacity expansion must pass the four tests',
 headers=['Fuel demand / domestic supply','HIGH supply','MEDIUM supply','LOW supply'],
 rows=[['LOW demand',
 'L / H\nDEFEND UTILISATION\nPrioritise low-capex efficiency.\nScreen rail access / EV adjacencies.',
 'L / M\nPHASE COMMITMENTS\nDebottleneck proven constraints.\nScreen EV adjacencies separately.',
 'L / L\nREPLACE LOST SUPPLY\nTest import corridor / rail access.\nAdd tanks only after the four tests.'],
 ['MEDIUM demand',
 'M / H\nCAPTURE DOMESTIC FLOWS\nTest inland / rail connections.\nDefer unsupported import expansion.',
 'M / M\nBASELINE CHOICE\nUse tanks better; price rail access.\nStage capacity behind contracts.',
 'M / L\nSECURE IMPORT ACCESS\nTest corridor / rail debottlenecks.\nExpand only at binding limits.'],
 ['HIGH demand',
 'H / H\nEXPAND DISTRIBUTION\nTest inland links and rail access.\nTank growth follows captured flow.',
 'H / M\nUNLOCK THROUGHPUT\nDebottleneck corridor / dispatch.\nAdd tanks if shortfall persists.',
 'H / L\nTEST STAGED EXPANSION\nSecure import / corridor capacity.\nTest rail access and extra tanks.']],
 caption='Each world: captured volume → route economics → required turns / bottleneck → investment option → return.',
 note='Qualitative priorities, not calculated recommendations. Rail options need volume, access and returns; rail freight recovery also changes fuel demand. EV adjacencies require a separate customer case and are not implied by low demand. Lever definitions remain in the appendix; original import-direction matrix retained in v22 and slide notes.')
page(5)['analysis_detail']='Original import-direction framework: '+json.dumps(json.loads((ROOT/'pptx/story/sa_market_story_v22_2026_10_08.json').read_text(encoding='utf-8'))['slides'][3]['rows'],ensure_ascii=False)

page(7)['rows'][0][2]='450m fewer litres in one year. Sustained recovery reduces diesel demand; retirements and replacement timing could reverse it.'
page(7)['rows'][1][2]='Road still carries 85.3% of tonnes. Rail recovery reduces diesel use only where freight transfers and net fuel savings follow.'
page(7)['rows'][2][2]='Agriculture grew; mining was flat and manufacturing declined. Sector activity matters more than one GDP assumption.'

page(9)['title']='Emerging Maputo and Walvis Bay routes must be tested alongside Durban and domestic supply'
page(9)['takeaway']='Maputo and Walvis Bay are emerging alternatives to include by destination. Compare delivered cost, capacity and reliable access before estimating how much inland demand Vopak can capture.'
page(9)['note']+=' Emerging alternatives are in scope; relative competitiveness is not yet quantified.'

page(14).update(title='Emerging gateways could redirect inland growth; delivered cost and reliable access determine capture',
headers=['Competing route','What changes the choice','Investment implication'],rows=[
 ['Durban–Lesedi','Pipeline, rail and road costs; reliable receipt and inland dispatch.','Test access and handling improvements that protect competitive customer supply.'],
 ['Maputo / Matola','Delivered cost, border time and capacity into each inland destination.','Include as an emerging alternative; test customer exposure and corridor responses.'],
 ['Walvis Bay','Distance, transit, border costs and feasible destination coverage.','Consider emerging inland opportunities; compare reach customer by customer.'],
 ['Domestic sources','Secunda / Natref availability, product output and distribution access.','Test inland handling and connections as well as import infrastructure.']],
note='Compare common product, destination, price date and tax basis. Emerging gateways must be considered; no relative cost ranking is asserted without quotes and verified access. Landlocked SADC opportunities require separate market/access evidence.')

page(15).update(title='Choose the investment that removes the proven constraint—and earns a return',
 headers=['Investment option','When it becomes relevant','Decision / commitment trigger'],
 icons=['turnover','transport','headroom','power'],icon_dir='output/delivered/sa_layout_2026_10_08_v16',rows=[
 ['Existing assets /\ndebottlenecking','Customer growth can be served through better tank turns, scheduling or receipt/dispatch.','Use available working capacity; invest in the specific bottleneck where incremental value is positive.'],
 ['Corridor / rail\naccess','Competitive customer flows are constrained by transport capacity, cost or reliability.','Secure service and volume commitments. Compare access contracts, loading assets and partnership investment.'],
 ['Additional\ntank capacity','Profitable captured flows exceed achievable handling and storage remains the binding constraint.','Size and stage tanks against contracted demand; pass the four tests and downside cases.'],
 ['EV-related\nadjacencies','Identified charging / fleet-energy customers offer a viable opportunity as transport electrifies.','Screen partnerships or dedicated assets separately: demand, power access, strategic fit and return must be proven.']],
 note='Investment menu, not approved projects. Network rail recovery is an external fuel-demand driver; Vopak rail loading/access is a distinct investment option. EV uptake reduces some fuel demand; it does not itself prove an EV investment case. Project costs, contracts and returns remain open.')

page(16)['title']='Resolve customer volume, working capacity and project economics first to determine the investment'
page(16)['rows']=[
 ['FIRST | Volume\nDR02 / DR05','Monthly unique deliveries, customer destination, contract term and contestable volumes; separate terminal transfers.','Establish the m³/year Vopak can secure and the revenue it supports.'],
 ['FIRST | Capacity\nDR03','Eligible working m³, actual turns, committed capacity, stock policy and receipt/dispatch limits.','Calculate the throughput shortfall and identify whether tanks, access or dispatch bind.'],
 ['FIRST | Economics\nDR04 / DR06','Matched delivered costs, access, rates, incremental costs and capex; hurdle, ramp-up and working capital.','Calculate route headroom, break-even volume and incremental return by option.'],
 ['THEN | Stress tests\nDR01 / DR07 / DR08','Reconciled product balance; annual demand, power and plant-output paths.','Test how far demand or supply must change before the preferred investment changes.'],
 ['SEPARATE | EV case\nDR09','Customer energy demand, charging utilisation, power connection, delivery partner, capex and contribution.','Decide whether an EV adjacency merits development on its own economics.']]
page(16)['note']='Request prepared, not sent. Sequence is proposed, not a quantified sensitivity ranking. Nigel to coordinate Vopak data; Manish to reconcile public evidence. Latest 36 complete months where available. Detailed requests and decision triggers logged; owners and commercial inputs remain to be confirmed.'

# Keep original lever detail in notes/appendix rather than expanding main-slide copy.
page(18)['rows'][3][1]='Rates, costs, capex and funding; separate EV adjacency economics.'
story.update(appendix_pages='17–34',cover_status='Investment conditions, nine-world priorities and targeted data requests; commercial thresholds remain open')
story['revision_23']={'changed_pages':[3,4,5,7,9,14,15,16,18],
 'added_page':34,'status':'Qualitative investment priorities; thresholds stated but uncalibrated',
 'authorisation':'User: show conditions and numbers; consider emerging gateways; include corridor/rail/EV investments; concise main story; prioritise and implement'}
(ROOT/'pptx/story/sa_market_story_v23_2026_10_08.json').write_text(json.dumps(story,ensure_ascii=False,indent=2),encoding='utf-8')

log=ROOT/'workstreams/WS0_governance/workplan/sa_investment_decisions_2026_10_08.csv'
rows=[
 ['Opening conditions','p3 recommendation; p4 four numeric gate rules','Captured/secured volume, cost headroom, operating shortfall and NPV not calibrated','Nigel / Vopak operations-commercial-finance','Before capital recommendation'],
 ['Emerging gateways','Maputo and Walvis Bay retained explicitly on p9/p14','Matched destination costs and accessible capacity unresolved','Manish / Nigel review','Before corridor ranking'],
 ['Nine-world investments','p5 cell-specific priorities; p15 option menu','No automatic rail or EV investment; all options require own economics','Manish / Nigel review','Before scenario recommendation'],
 ['Main-story concision','SCR detail moved to p34; lever codes removed from decision-facing copy','Source qualifications retained','Nigel review','At next story review'],
 ['Priority data','p16 volume/capacity/economics first; DR09 EV-specific request','Priority is judgement; quantitative reversal sensitivity awaits inputs','Nigel to coordinate','At receipt of first commercial data']]
with log.open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['change','implemented','open_condition','proposed_owner','trigger']);w.writerows(rows)
request=ROOT/'output/delivered/investment_bridge_2026_10_08/data_request.csv'
with request.open(encoding='utf-8',newline='') as f:r=csv.DictReader(f);fields=r.fieldnames;req=list(r)
if not any(r['id']=='DR09' for r in req):
    req.append(dict(zip(fields,['DR09','P2','EV adjacency','Separate EV investment case','Customer energy and charging demand; utilisation by location; power connection and tariff; capex, costs, commercial terms, partner model and strategic mandate','Nigel to coordinate','Potential customers / Vopak strategy / power partners','Before EV investment screening','Standalone customer, power-access and incremental-return case; not inferred from low fuel demand','Prepared; not sent','',''])))
    with request.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(req)
print('Prepared v23 decision story and change log; no new numeric assumptions introduced')
