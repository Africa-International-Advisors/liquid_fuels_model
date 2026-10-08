"""Populate the story from a reproducible, explicitly illustrative investment case."""
from copy import deepcopy
import csv,hashlib,json
from pathlib import Path
from lfm.governance import inventory
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/delivered/vopak_illustration_2026_10_08'
d=json.loads((OUT/'results.json').read_text());a=d['assumptions'];r=d['reported'];case=d['anchor']
story=json.loads((ROOT/'pptx/story/sa_market_story_v23_2026_10_08.json').read_text(encoding='utf-8'))
def page(n):return story['slides'][n-2]
def bn(x):return f'{x/1e6:.3f}'
def rm(x):return f'{x/1e6:+.0f}'
threshold=d['reversal_captured_m3']
page(3)['rows'][1][1]='The worked illustration favours existing assets in six worlds; access/dispatch improvement in two.'
page(3)['rows'][2][1]='Only high demand / low domestic supply favours extra tanks, with a narrow advantage over improvement alone.'
page(3)['rows'][3][2]='Validate capture, chargeable revenues and capex first; the illustrated choice reverses under downside tests.'
page(3)['note']='Working recommendation supported by an authored Lesedi illustration, not a calibrated forecast. Reported capacity is used; capture, working capacity, tariffs, capex and discount rate are assumptions. No customer volume is represented as secured.'
page(4).update(title='The illustrated expansion case passes narrowly—and depends on capture, revenue and capex',
 headers=['Decision test','Numeric condition','ILLUSTRATIVE high / low case','Still needs verification'],
 rows=[
 ['Customer\nvolume','Tanks must outperform improving existing capacity.','Assumed capture '+bn(case['captured_lesedi_m3'])+'bn L/year; tanks win above '+bn(threshold['tanks_vs_improvement'])+'bn L/year.','No secured volumes inferred. Validate customer capture and contract duration.'],
 ['Route\neconomics','Delivered-cost headroom ≥ R0/m³.','R750 allowable less R650 assumed logistics = R100/m³ headroom.','Both prices are authored. Compare actual Durban, Maputo, Walvis Bay and domestic quotes.'],
 ['Capacity\nconstraint','Captured flow exceeds achievable handling.','Existing '+bn(case['existing_limit_m3'])+'bn L/year; improvement '+bn(case['improved_limit_m3'])+'bn; tanks '+bn(case['options'][2]['achievable_annual_m3'])+'bn.','90% working capacity and 1.25 / 1.50 monthly turns are assumptions, not reported operations.'],
 ['Incremental\nreturn','Positive NPV and better value than the alternative.','Improvement NPV R'+rm(case['options'][1]['npv_zar'])+'m; combined R'+rm(case['options'][2]['npv_zar'])+'m. Extra advantage only R'+f"{(case['options'][2]['npv_zar']-case['options'][1]['npv_zar'])/1e6:.0f}"+'m.','10% discount rate, 20 years, pre-tax. Actual tariffs, cost, tax and project schedule remain open.']],
 note='ILLUSTRATIVE ONLY. 100% project basis, constant ZAR; capex at t0; operating ramp 50%/75%/100%; no tax, working capital, construction delay, inflation or residual value. Turnover and occupancy are distinct. Full assumptions, benchmarks, options and downside tests: pp35–38.')

choices={'Existing':'USE EXISTING ASSETS','Improve access / dispatch':'IMPROVE ACCESS / DISPATCH','Improve + add tanks':'TEST IMPROVEMENT + TANKS'}
matrix=[]
for demand in ('Low','Medium','High'):
    row=[demand.upper()+' demand\n'+f"{a['demand_bn_l'][demand]:.1f}bn L/year"]
    for supply in ('High','Medium','Low'):
        w=next(x for x in d['worlds'] if x['demand_world']==demand and x['supply_world']==supply)
        row.append(f"{demand[0]} / {supply[0]}"+(' | BASELINE' if demand==supply=='Medium' else '')+'\n'+choices[w['preferred_option']]+f"\nCapture {w['captured_lesedi_m3']/1e6:.2f}bn L/year"+f"\nIncremental NPV R{w['preferred_npv_zar']/1e6:+.0f}m")
    matrix.append(row)
page(5).update(title='Only one illustrative world favours tanks; six favour existing assets and two favour improvement',
 headers=['Gauteng demand /\ndomestic supply','HIGH deliveries\n4.8bn L/year','MEDIUM deliveries\n3.6bn L/year','LOW deliveries\n2.4bn L/year'],rows=matrix,
 caption='Highest incremental NPV among three illustrative packages; R0 means retain existing assets, not zero terminal value.',
 note='ILLUSTRATIVE snapshot, not forecast or probabilities. Domestic supply here means assumed deliveries into Gauteng, not national refinery capacity. Shares, rates and costs held fixed across worlds. Rail/EV opportunities remain separate cases, not valued here. Each cell is relative to existing assets; unserved volumes can remain. Inputs: p37; downside: p38.')
page(5)['analysis_detail']+='\nThe nine numerical cells use an authored regional supply-delivery bridge, not calibrated national refinery output. Original qualitative rail/EV investment priorities remain in v23 and p15.'
page(10)['note']+=' Separate p4/p5 illustration assumes 90% working capacity and 1.25/1.50 turns; neither is inferred from group occupancy.'
page(15)['note']+=' Three fuel-logistics packages are priced illustratively on p35; these do not constitute engineered rail or EV project estimates.'
page(16)['rows'][0][2]='Test the illustrated 2.21bn L improvement trigger and 2.806bn L tank trigger against actual customer commitments.'
page(16)['rows'][2][2]='Replace the authored rent, chargeable-service margin and capex; these determine whether the narrow expansion advantage survives.'

def table_slide(title,headers,rows,note,widths=None):
    return dict(title=title,section=0,headers=headers,rows=rows,note=note,column_widths=widths or [175,325,338.8],font_size=12,title_font_size=23.0)
option_rows=[]
for o in case['options']:
    option_rows.append([o['option'],f"R{o['capex_zar']/1e6:.0f}m capex\n{o['served_m3']/1e6:.3f}bn L/year served",f"NPV R{o['npv_zar']/1e6:+.1f}m\nUnserved {o['unserved_m3']/1e6:.3f}bn L/year"])
option_rows.append(['Decision threshold','Improvement beats existing above '+bn(threshold['improvement_vs_existing'])+'bn L/year.','Tanks beat improvement above '+bn(threshold['tanks_vs_improvement'])+'bn L/year; assumed capture '+bn(case['captured_lesedi_m3'])+'bn.'])
story['slides'].append(table_slide('The illustration gives extra tanks only R8m more NPV than improvement alone',
 ['High demand / low supply','Capital and throughput','Incremental value versus existing'],option_rows,
 'ILLUSTRATIVE ONLY. Combined package = R100m access/dispatch improvement + R500m for a further 40,000 gross m³ beyond the reported 140,000 m³. Alternatives are authored packages, not engineered designs. Full incremental pre-tax cash flows in delivered CSV; 100% site basis. NPV uses 10% and 20 operating years; commercial and delivery risks uncalibrated.'))
story['slides'].append(table_slide('Vopak reports anchor capacity and the revenue model; they do not disclose Lesedi project economics',
 ['Evidence class','What the sources establish','How it is used'],[
 ['REPORTED | Assets','Lesedi: 140,000 m³; Durban: 360,246 m³. Vopak share: 70% at each site.','Use full physical capacity for operations. Annual report confirms Lesedi expansion was commissioned in 2025.'],
 ['REPORTED | Revenue','Storage services: EUR1,058.8m of EUR1,298.9m consolidated revenue in 2025.','81.5% is storage revenue. Rental may include minimum throughput; extra turns are not automatically extra revenue.'],
 ['INFERRED | Group ratio',f"EUR{d['inferred']['group_revenue_per_proportional_capacity_eur_year']:.1f} revenue / gross m³/year: proportional revenue divided by year-end proportional capacity.",'Mixed-portfolio scale indicator only. Not a Lesedi tariff, margin or estimate of site revenue.'],
 ['REPORTED | Benchmarks','15.6% group operating cash return; 5–7x capex/EBITDA for gas/industrial and 4–8x for transition infrastructure.','Context, not South Africa fuel-project hurdle rates. Authored 10% discount rate is separate.']],
 'Vopak Annual Report 2025 pp36/39, 63, 213 and 324; FY2025 Analyst Presentation p24; official terminal directory checked 8 Oct 2026. All other business units includes multiple countries; do not allocate its profit to South Africa. URLs, downloaded originals and hashes retained.'))
story['slides'].append(table_slide('The investment result rests on explicit assumptions that must be replaced or agreed',
 ['ILLUSTRATIVE input','Value used','What must be validated'],[
 ['Catchment balance','Demand 6.0 / 6.8 / 7.6bn L; domestic deliveries 2.4 / 3.6 / 4.8bn L.','Steady-state stress points; M rounds 2022 Gauteng sales for scale. No national production forecast implied.'],
 ['Capture','70% of imports via Durban; Vopak captures 80%; 90% goes to Lesedi; 8% domestic capture.','No observed shares. Capture is unique Lesedi flow; Durban transfers are not added to market demand.'],
 ['Operations','90% working fraction; turns 1.25 existing / 1.50 improved; +40,000 gross m³ tanks.','126,000 working m³ initially; 162,000 with tanks. Assumed receipt/dispatch ceiling 3.5bn L/year.'],
 ['Revenue','R1,500 / gross m³/year rent on added contracted tanks; R60 / extra m³ contribution.','Chargeable excess services only, excluding rent/minimum-throughput inclusions. Added rent follows incremental storage use.'],
 ['Capital and costs','R100m improvement + R500m tanks; fixed opex R5m + R12m/year; maintenance 1% capex/year.','Author-selected cost sensitivities; no Vopak quotation or engineering estimate.'],
 ['Cash flow','20 years at 10%; 50% / 75% / 100% operating ramp; capex upfront.','Pre-tax unlevered constant ZAR. Tax, working capital, construction timing and residual value excluded.']],
 'Every illustrative value is registered in assumptions/2026/vopak_investment_illustration.yaml. Not a forecast, commercial offer or approval. Proposed validation: Nigel coordinates Vopak commercial/operations; Manish reconciles; independent review outstanding.'))
story['slides'].append(dict(title='Small changes in capture or economics overturn the illustrated tank-expansion choice',section=0,
 custom_chart='output/delivered/vopak_illustration_2026_10_08/sensitivity.png',title_font_size=23.0,
 takeaway='The illustration supports validating contracts and a low-capex improvement first. Extra tanks have only a narrow advantage and fail the tested downside cases.',
 note='ILLUSTRATIVE high-demand/low-domestic-delivery case. NPVs are incremental versus existing assets at 10%, pre-tax. Each shock applied separately: capex +25%; no chargeable excess services; Vopak gateway capture 80%→60%; captured Lesedi flow −10%. No probabilities. Full numeric outputs and cash flows retained.'))
story.update(appendix_pages='17–38',cover_status='Reported Vopak context and illustrative investment economics; all commercial assumptions require validation')
story['revision_24']={'status':'Illustrative only','changed_pages':[3,4,5,10,15,16],'added_pages':[35,36,37,38],
 'source':'Vopak Annual Report 2025 and FY2025 analyst presentation; terminal directory','user_authorisation':'Build story with data and illustrative values; use annual reports to infer'}
(ROOT/'pptx/story/sa_market_story_v24_2026_10_08.json').write_text(json.dumps(story,indent=2,ensure_ascii=False),encoding='utf-8')

# A visual comparison generated solely from calculated results.
navy='#0A2373';blue='#849BC1';grey='#666666'
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="880" height="340" viewBox="0 0 880 340"><rect width="880" height="340" fill="white"/>',
 '<text x="0" y="18" font-family="Lato" font-size="15" font-weight="bold">ILLUSTRATIVE incremental NPV, Rm</text>']
low=-750;high=100;x0=230;width=560
def px(v):return x0+(v-low)/(high-low)*width
for tick in [-750,-500,-250,0]:
    x=px(tick);parts.append(f'<line x1="{x}" y1="45" x2="{x}" y2="303" stroke="#dddddd"/><text x="{x}" y="322" text-anchor="middle" font-size="12" font-family="Lato" fill="#666">{tick}</text>')
for i,row in enumerate(d['sensitivity']):
    y=62+i*49
    label=row['case'].replace('No chargeable excess services','No excess-service charges')
    parts.append(f'<text x="0" y="{y+11}" font-family="Lato" font-size="13">{label}</text>')
    for j,col in [(1,blue),(2,navy)]:
        value=row['options'][j]['npv_zar']/1e6;yy=y+(j-1)*17
        left=min(px(0),px(value));bar=abs(px(value)-px(0))
        parts.append(f'<rect x="{left}" y="{yy}" width="{max(bar,1)}" height="12" fill="{col}"/><text x="{px(value)-5 if value<0 else px(value)+5}" y="{yy+11}" text-anchor="{"end" if value<0 else "start"}" font-family="Lato" font-size="12" fill="{col}">{value:+.1f}</text>')
parts.extend([f'<rect x="500" y="8" width="11" height="11" fill="{blue}"/><text x="516" y="18" font-family="Lato" font-size="12">Improvement</text>',f'<rect x="650" y="8" width="11" height="11" fill="{navy}"/><text x="666" y="18" font-family="Lato" font-size="12">Improvement + tanks</text>','</svg>'])
(OUT/'sensitivity.svg').write_text(''.join(parts),encoding='utf-8')

# Governance: append only this new block, never relabel assumptions as verified.
reg=ROOT/'governance/assumption_register.csv'
with reg.open(encoding='utf-8-sig',newline='') as f:reader=csv.DictReader(f);cols=reader.fieldnames;rows=list(reader)
exists={x['assumption'] for x in rows}
for item in inventory():
    if item['block'].startswith('vopak_investment_illustration.') and item['assumption'] not in exists:
        row={k:item.get(k,'') for k in cols};row.update(id='LOC-'+hashlib.sha256(item['assumption'].encode()).hexdigest()[:12],review_status='unreviewed');rows.append(row)
with reg.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
ep=ROOT/'governance/exception_log.csv'
with ep.open(encoding='utf-8-sig',newline='') as f:reader=csv.DictReader(f);cols=reader.fieldnames;rows=list(reader)
if not any(x['id']=='EXC-VOPAK-ILLUSTRATION' for x in rows):
    values=dict(id='EXC-VOPAK-ILLUSTRATION',assumption='vopak_investment_illustration.*; model.illustrative_investment',reason='User-authorised illustration combines reported context with author-selected regional delivery/capture/operating/commercial inputs. Not calibrated or forecast-integrated.',owner='nigel.zhuwaki',risk='Group statistics may be mistaken for terminal economics; rental inclusions may double-count throughput revenue; unvalidated capture/capex/ramp/tax assumptions may reverse investment choices.',expiry_trigger='Before client investment reliance or adoption as a forecast; review when DR02-DR06 received',expires_on='2026-11-12',migration_path='Replace authored shares, working capacity, chargeable services, costs and hurdle; reconcile domestic access and coastal allocation; engineer alternatives; include tax, working capital and construction timing; independently review.',status='open',validity='2026')
    rows.append({k:values.get(k,'') for k in cols})
with ep.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
log=ROOT/'workstreams/WS0_governance/workplan/sa_illustrative_investment_2026_10_08.csv'
with log.open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f);w.writerow(['item','implemented','classification','remaining','proposed_owner','trigger'])
    w.writerows([
      ['Vopak evidence','Annual report and investor presentation retained; pages and hashes recorded','Reported / derived','Independent source review; no country P&L allocation','Manish','Before model adoption'],
      ['Nine worlds','Explicit regional demand/delivery and capture assumptions produce terminal flow','Illustrative','Replace shares and annual paths; verify domestic access and Durban capacity','Manish / Nigel','Before forecast or market-share publication'],
      ['Investment packages','Incremental rent/services/cost cash flows for existing, improvement and combined tanks','Illustrative','Engineering quotes, contract inclusions, tax/working capital/construction timing','Nigel / Vopak','Before investment recommendation'],
      ['Reversal tests','Capex, service revenue and capture downside calculated; thresholds shown on p4','Calculated from illustrative inputs','Confirm which parameters and alternatives matter with actual data','Nigel / independent review','At first commercial-data handback']])
print('Prepared v24: numeric gates/worlds plus source, assumption, option and sensitivity appendix; assumptions registered')
