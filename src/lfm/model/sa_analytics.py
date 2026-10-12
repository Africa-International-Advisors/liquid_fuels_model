"""Auditable 2025 baseline and scenario arithmetic. No file or network I/O.

The cell graph is the single calculation definition for Python results and Excel.
It deliberately preserves an unexplained supply-demand difference.
"""
import re
from dataclasses import dataclass, field

@dataclass
class Book:
    sheets: dict = field(default_factory=dict)
    cells: dict = field(default_factory=dict)
    def sheet(self,name,title,headers,widths=None):
        self.sheets[name]={'title':title,'headers':headers,'rows':[],'widths':widths or [34]+[17]*(len(headers)-2)+[65]}
    def row(self,s,values):
        r=len(self.sheets[s]['rows'])+5
        self.sheets[s]['rows'].append(values)
        for c,v in enumerate(values): self.cells[(s,f'{chr(65+c)}{r}')]=v
        return r
    def ref(self,s,r,c='B'): return f"'{s}'!{c}{r}"
    def fx(self,s,r,c,formula):
        def sub(m):
            sh=m.group(1) or s
            value=self.cells[(sh,m.group(2).replace('$',''))]
            if isinstance(value,dict): value=value['value']
            if not isinstance(value,(int,float)): raise ValueError((sh,m.group(2),value))
            return repr(value)
        exp=re.sub(r"(?:'([^']+)'!)?(\$?[A-Z]+\$?\d+)",sub,formula.lstrip('='))
        value=eval(exp,{'__builtins__':{}},{'MIN':min,'MAX':max})
        cell={'formula':'='+formula.lstrip('='),'value':value}
        self.sheets[s]['rows'][r-5][ord(c)-65]=cell
        self.cells[(s,f'{c}{r}')]=cell
        return self.ref(s,r,c)
    def val(self,ref):
        sh,cell=ref.split('!');v=self.cells[(sh.strip("'"),cell)]
        return v['value'] if isinstance(v,dict) else v

def build(payload, planning_case=None):
    b=Book();e={};a={};case_refs={}
    b.sheet('Summary','South Africa fuel baseline and outlook',['Measure','Value','Unit','Interpretation'],[43,20,20,105])
    b.sheet('Demand history','Reported demand and the estimated 2025 baseline',['Year','Petrol bn L','Diesel bn L','Total bn L','Basis'],[12,18,18,18,100])
    b.sheet('Segments','2025 demand by use',['Segment','2023 bn L','2024 bn L','2025 bn L','2023-25 change','Treatment'],[36,18,18,18,19,100])
    b.sheet('Plant supply','2025 domestic petrol and diesel supply estimate',['Plant','All products bn L','Petrol yield','Diesel yield','Petrol bn L','Diesel bn L','Total P+D bn L','Basis'],[28,21,18,18,18,18,20,95])
    b.sheet('Balance','Demand and supply reconciliation',['Measure','Petrol bn L','Diesel bn L','Total bn L','Treatment'],[43,19,19,19,105])
    b.sheet('Scenarios','2025-2030 demand and import sensitivities',['Case / year','Demand bn L','Supply bn L','Gross import need bn L','Change vs 2025 bn L','Trade-anchored bn L','Added Moz flow bn L','Imports ex-Moz proxy bn L','Meaning'],[23,18,18,23,23,23,21,25,90])
    b.sheet('Driver bridge','2030 volume changes by driver',['Case','Activity bn L','Efficiency bn L','Rail net bn L','Power bn L','Operating supply bn L','Restart supply bn L','Net import change bn L','Basis'],[22,20,20,20,20,24,23,25,90])
    b.sheet('Mozambique','Mozambique nodes and route economics',['Item','Value','Unit','Basis / source'],[43,22,24,110])
    b.sheet('Assumptions','Editable analytical assumptions',['Assumption','Value','Unit / basis','Interpretation'],[47,20,43,95])
    b.sheet('Evidence','Frozen source observations',['Input','Value','Unit','Source / period'],[48,22,28,115])
    for k,v in payload['evidence'].items():
        r=b.row('Evidence',[k,v['value'],v['unit'],v['source']+'; '+v['basis']]);e[k]=b.ref('Evidence',r)
    for k,v in payload['assumptions'].items():
        meaning='Analyst sensitivity; not measured or independently approved'
        if k.startswith('private_power'): meaning='Assumed private backup within national demand; allocation replaces part of other use, not additional national volume'
        if k.startswith('natref_'): meaning='FY2025 Sasol output / 63.64% ownership; product yields use midpoints of published 2021 ranges'
        if k.startswith('secunda_'): meaning='Assume 90% of refined products are petrol/diesel; published approximate 65/35 split applied within that subset'
        if k.startswith('astron_'): meaning='Convert all-product energy to litres, then assume 80% petrol/diesel and 50/50 volume mix'
        if k=='eskom_diesel_share': meaning='Upper-bound simplification: diesel + kerosene treated as diesel; calendar year proxied by March financial year'
        if k=='unreported_construction_bn': meaning='Zero subtraction when no construction row is reported; does not establish zero construction use. Affects industry residual.'
        unit='fraction' if any(x in k for x in ['share','fraction','growth','efficiency','yield','rate','allocation']) else 'value'
        if k.startswith('private_power') or k.endswith('_bn'):unit='bn litres'
        elif k.endswith('_km'):unit='km' if 'cost' not in k else 'ZAR/km'
        elif k.endswith('_zar_l'):unit='ZAR/litre'
        elif k.endswith('_zar_day'):unit='ZAR/day'
        elif k.endswith('_bpd'):unit='barrels/day'
        elif k.endswith('_m3'):unit='m3'
        elif k.endswith('_days'):unit='days'
        elif k.endswith('_litres'):unit='litres'
        elif k.endswith('_turns'):unit='turns/month'
        elif k=='ipp_litres_per_kwh':unit='litres/kWh'
        elif k=='barrel_litres':unit='litres/barrel'
        elif k=='btu_mj':unit='MJ/Btu'
        elif k=='astron_mj_per_litre':unit='MJ/litre'
        elif k=='outlook_year':unit='year'
        r=b.row('Assumptions',[k,v,unit,meaning]);a[k]=b.ref('Assumptions',r)
    for case,vals in payload['scenarios'].items():
        case_refs[case]={}
        for k,v in vals.items():
            r=b.row('Assumptions',[case+': '+k,v,'Fraction / year / bn L as named','Authored 2030 sensitivity, not a project forecast or probability; rail shift is eligible road-freight tonne-km share'])
            case_refs[case][k]=b.ref('Assumptions',r)
    hist={}
    for y in range(2013,2024):
        r=b.row('Demand history',[y,None,None,None,'Department reported sales; national petrol and diesel'])
        for c,p in [('B','petrol'),('C','diesel')]:b.fx('Demand history',r,c,e[f'sales_{p}_{y}'])
        b.fx('Demand history',r,'D',f'B{r}+C{r}');hist[y]=r
    # Separate utility/private power estimates used consistently in annual bridges.
    power={}
    for y in (2023,2024,2025):
        r=b.row('Assumptions',[f'Calculated power {y}',None,'bn L','Eskom fuel FY proxy x diesel fraction + IPP GWh x 0.31 L/kWh + assumed private backup'])
        power[y]=b.fx('Assumptions',r,'B',f'{e[f"eskom_{y}"]}*{a["eskom_diesel_share"]}+{e[f"ipp_gwh_{y}"]}*{a["ipp_litres_per_kwh"]}/1000+{a[f"private_power_{y}"]}')
    for y in (2024,2025):
        prev=hist[y-1];r=b.row('Demand history',[y,None,None,None,'Estimate from Department 2023 anchor; power FY proxy; explicit activity and efficiency assumptions'])
        b.fx('Demand history',r,'B',f'B{prev}*(1+{a["petrol_activity_growth"]})*(1-{a["petrol_efficiency_change"]})')
        b.fx('Demand history',r,'C',f'(C{prev}-{power[y-1]})*(1+{a["nonpower_diesel_growth"]})+{power[y]}')
        b.fx('Demand history',r,'D',f'B{r}+C{r}');hist[y]=r
    alt=b.row('Demand history',['2024 FIASA',None,None,None,'Alternative source; not spliced into the Department series'])
    b.fx('Demand history',alt,'B',e['fiasa_petrol_2024']);b.fx('Demand history',alt,'C',e['fiasa_diesel_2024']);b.fx('Demand history',alt,'D',f'B{alt}+C{alt}')
    alt25=b.row('Demand history',['2025 alternative',None,None,None,'Same drivers applied to 2024 FIASA anchor; source-choice sensitivity'])
    b.fx('Demand history',alt25,'B',f'B{alt}*(1+{a["petrol_activity_growth"]})*(1-{a["petrol_efficiency_change"]})')
    b.fx('Demand history',alt25,'C',f'(C{alt}-{power[2024]})*(1+{a["nonpower_diesel_growth"]})+{power[2025]}');b.fx('Demand history',alt25,'D',f'B{alt25}+C{alt25}')
    seg={}
    def segment(name,formula,note):
        r=b.row('Segments',[name,None,None,None,None,note]);seg[name]=r
        for c,y in [('B',2023),('C',2024),('D',2025)]:b.fx('Segments',r,c,formula(y,c))
        b.fx('Segments',r,'E',f'D{r}-B{r}');return r
    segment('Petrol road use',lambda y,c:f'{b.ref("Demand history",hist[y],"B")}*{a["petrol_road_share"]}','97% road-use allocation; includes cars and commercial vehicles, not passenger-only')
    for sector in ('mining','manufacturing','agriculture'):
        terms=[]
        for y in range(2018,2022):
            vol=e[f'eb_{sector}_{y}'] if sector!='manufacturing' else f'({e[f"eb_industry_{y}"]}-{e[f"eb_mining_{y}"]}-{e.get(f"eb_construction_{y}",a["unreported_construction_bn"])})'
            terms.append(f'({vol}/{e[f"{sector}_activity_{y}"]})')
        intensity='('+'+'.join(terms)+')/4'
        segment(sector.title(),lambda y,c,sector=sector,intensity=intensity:f'({intensity})*{e[f"{sector}_activity_{y}"]}','2018-2021 mean fuel/activity intensity x annual activity; manufacturing is industry less mining and construction. Sector road use retained here.')
    segment('Utility and private power',lambda y,c:power[y],'FY utility proxy; private backup 0.8/0.6/0.2bn L in 2023/24/25 is an assumption. No addition to national total.')
    road23=f'{e["eb_road_2021"]}*(1+{a["nonpower_diesel_growth"]})^2'
    # ^ is Excel power; graph evaluator uses ** below.
    road23=road23.replace('^','**')
    def road(y):
        if y==2023:return road23
        if y==2024:return f'({road23})*(1+{a["nonpower_diesel_growth"]})*(1-{a["road_diesel_efficiency_change"]})'
        return f'({road(2024)})*({e["freight_road_2025"]}/{e["freight_road_2024"]})*(1-{a["road_diesel_efficiency_change"]})'
    segment('Road freight diesel',lambda y,c:f'({road(y)})*{a["road_diesel_freight_share"]}','75% assumed share of road diesel. Road excludes sector-attributed purchases by convention; 2025 all-goods tonnes proxy activity, constant distance/mix.')
    segment('Other road diesel',lambda y,c:f'({road(y)})*(1-{a["road_diesel_freight_share"]})','Passenger, light commercial and buses; complementary share of road diesel')
    petrol_other=segment('Other petrol',lambda y,c:f'{b.ref("Demand history",hist[y],"B")}*(1-{a["petrol_road_share"]})','Complement of assumed road petrol share')
    prior_diesel=[r for n,r in seg.items() if n not in ('Petrol road use','Other petrol')]
    segment('Other diesel / unallocated',lambda y,c:f'{b.ref("Demand history",hist[y],"C")}-'+'-'.join(f'{c}{r}' for r in prior_diesel),'Explicit residual: commercial/public, construction, rail, marine and classification differences. Not assigned to freight or manufacturing.')
    total=segment('Total',lambda y,c:'+'.join(f'{c}{r}' for r in list(seg.values())[:-1]),'Reconciles to independent national demand estimate; detailed use allocation remains estimated')
    check=segment('Allocation less national total',lambda y,c:f'{c}{total}-{b.ref("Demand history",hist[y],"D")}','Arithmetic reconciliation; zero does not establish empirical sector coverage')
    plants={}
    for plant in ('Secunda','Natref','Astron','SAPREF','PetroSA','Enref'):
        r=b.row('Plant supply',[plant,None,None,None,None,None,None,'']);plants[plant]=r
        if plant=='Secunda':
            vol=f'{e["output_Secunda_2025"]}*{a["barrel_litres"]}/1000';p=f'{a["secunda_pd_share"]}*{a["secunda_petrol_share_of_pd"]}';d=f'{a["secunda_pd_share"]}*(1-{a["secunda_petrol_share_of_pd"]})';note='FY2025 all-refined-products proxy for calendar 2025; excludes chemical output'
        elif plant=='Natref':
            vol=f'{e["output_Natref_2025"]}/{a["natref_share"]}*{a["barrel_litres"]}/1000';p=a['natref_petrol_yield'];d=a['natref_diesel_yield'];note='FY2025 share basis only. FY2026 includes above-share output and is not mechanically grossed up.'
        elif plant=='Astron':
            vol=f'{e["output_Astron_2025"]}*{a["btu_mj"]}/{a["astron_mj_per_litre"]}';p=f'{a["astron_pd_share"]}*{a["astron_petrol_share_of_pd"]}';d=f'{a["astron_pd_share"]}*(1-{a["astron_petrol_share_of_pd"]})';note='Calendar 2025 billion Btu converted to bn litres; energy density and product split assumed'
        else:vol=p=d='0';note='No refining output in 2025; terminal activity is not production'
        b.sheets['Plant supply']['rows'][r-5][7]=note
        for c,f in [('B',vol),('C',p),('D',d),('E',f'B{r}*C{r}'),('F',f'B{r}*D{r}'),('G',f'E{r}+F{r}')]:b.fx('Plant supply',r,c,f)
    pr=b.row('Plant supply',['Total',None,None,None,None,None,None,'Petrol/diesel subset only; plant production is estimated, not national reported output'])
    for c in ('B','E','F','G'):b.fx('Plant supply',pr,c,'+'.join(f'{c}{r}' for r in plants.values()))
    supply_petrol=b.ref('Plant supply',pr,'E');supply_diesel=b.ref('Plant supply',pr,'F')
    if planning_case:
        b.sheet('Supply assumption','Directed domestic production planning case',['Measure','Value','Unit','Treatment'],[45,22,22,105])
        selected=b.row('Supply assumption',['Selected national production',planning_case['domestic_petrol_diesel_bn_l'],'bn L','User-directed planning assumption, 11 October 2026; not reported production'])
        mix=b.row('Supply assumption',['Petrol fraction',None,'fraction','Original plant-estimate mix retained provisionally; no product-balance calibration'])
        b.fx('Supply assumption',mix,'B',f'{b.ref("Plant supply",pr,"E")}/{b.ref("Plant supply",pr,"G")}')
        petrol=b.row('Supply assumption',['Allocated petrol production',None,'bn L','Planning allocation only'])
        supply_petrol=b.fx('Supply assumption',petrol,'B',f'B{selected}*B{mix}')
        diesel=b.row('Supply assumption',['Allocated diesel production',None,'bn L','Planning allocation only'])
        supply_diesel=b.fx('Supply assumption',diesel,'B',f'B{selected}-B{petrol}')
        original=b.row('Supply assumption',['Original plant-based estimate',None,'bn L','Reference sensitivity; does not govern this planning case'])
        b.fx('Supply assumption',original,'B',b.ref('Plant supply',pr,'G'))
    balances={}
    def balance(label,petrol,diesel,note):
        r=b.row('Balance',[label,None,None,None,note]);balances[label]=r
        b.fx('Balance',r,'B',petrol);b.fx('Balance',r,'C',diesel);b.fx('Balance',r,'D',f'B{r}+C{r}');return r
    dr=balance('2025 demand',b.ref('Demand history',hist[2025],'B'),b.ref('Demand history',hist[2025],'C'),'Department anchored estimate')
    sr=balance('Domestic production',supply_petrol,supply_diesel,'User-directed 5.8bn planning case; provisional product split' if planning_case else 'Plant-output estimate with explicit product yields')
    ir=balance('Gross customs imports',e['trade_All_import_petrol_2025'],e['trade_All_import_diesel_2025'],'Recorded litres, calendar 2025')
    xr=balance('Customs exports',e['trade_All_export_petrol_2025'],e['trade_All_export_diesel_2025'],'Recorded litres, calendar 2025')
    ar=balance('Supply plus net imports',f'B{sr}+B{ir}-B{xr}',f'C{sr}+C{ir}-C{xr}','Availability before stock changes and statistical/scope differences')
    gap=balance('Unexplained availability less demand',f'B{ar}-B{dr}',f'C{ar}-C{dr}','Not assigned to stocks or concealed in demand; investigate sales coverage, FY conversion, yields, customs scope and re-exports')
    need=balance('Demand-implied gross imports',f'B{dr}-B{sr}+B{xr}',f'C{dr}-C{sr}+C{xr}','Zero stock-change assumption; not reconciled to customs imports')
    balance('FIASA-anchor alternative demand',b.ref('Demand history',alt25,'B'),b.ref('Demand history',alt25,'C'),'Source-choice sensitivity only')
    balance('Domestic output implied by demand/trade',f'B{dr}-B{ir}+B{xr}',f'C{dr}-C{ir}+C{xr}','Zero stock change. Compare this implied output with the plant estimate; it is not a replacement production assumption.')
    bridges={};scenario_rows={}
    D=b.ref('Balance',dr,'D');S=b.ref('Balance',sr,'D');I=b.ref('Balance',ir,'D');X=b.ref('Balance',xr,'D')
    P=b.ref('Segments',seg['Utility and private power'],'D');F=b.ref('Segments',seg['Road freight diesel'],'D')
    roadtotal=f'({b.ref("Segments",seg["Petrol road use"],"D")}+{F}+{b.ref("Segments",seg["Other road diesel"],"D")})'
    for case,v in case_refs.items():
        for y in range(2025,2031):
            t=y-2025;frac=t/5
            activity=f'({D}-{P})*((1+{v["activity_growth"]})**{t}-1)'
            efficiency=f'-{roadtotal}*(1+{v["activity_growth"]})**{t}*(1-(1-{v["efficiency"]})**{t})'
            rail=f'-{F}*(1+{v["activity_growth"]})**{t}*(1-{v["efficiency"]})**{t}*{v["rail_shift"]}*{frac}*(1-{v["rail_diesel_rebound"]})'
            powerchange=f'-{P}*(1-{v["power_retained"]})*{frac}'
            operating=f'{S}*({v["supply_multiplier"]}-1)*{frac}'
            restarts=[]
            for plant in ('sapref','petrosa'):
                # Dates are authored scenario assumptions; ramp reaches target after two years.
                ramp=f'MIN(1,MAX(0,({y}-{v[plant+"_start"]}+1)/2))'
                restarts.append(f'{a[plant+"_bpd"]}*365*{a["barrel_litres"]}/1000000000*{a["restart_pd_yield"]}*{v[plant+"_utilisation"]}*{ramp}')
            restart='+' .join(restarts)
            r=b.row('Scenarios',[case+' '+str(y),None,None,None,None,None,None,None,'Gross imports = demand - domestic supply + fixed 2025 exports; zero stock change. Trade anchor preserves the unresolved 2025 gap.'])
            b.fx('Scenarios',r,'B',f'{D}+({activity})+({efficiency})+({rail})+({powerchange})')
            b.fx('Scenarios',r,'C',f'{S}+({operating})+({restart})')
            b.fx('Scenarios',r,'D',f'B{r}-C{r}+{X}')
            b.fx('Scenarios',r,'E',f'D{r}-{b.ref("Balance",need,"D")}')
            b.fx('Scenarios',r,'F',f'{I}+E{r}')
            b.fx('Scenarios',r,'G',f'{v["moz_diversion_bn"]}*{frac}')
            b.fx('Scenarios',r,'H',f'F{r}-G{r}-{e["trade_Komatipoort_import_petrol_2025"]}-{e["trade_Komatipoort_import_diesel_2025"]}')
            b.sheets['Scenarios']['rows'][r-5][8]+=' Ex-Moz proxy deducts 2025 Komatipoort flow and additional diversion; other border routes remain, so this is not port throughput or Vopak demand.'
            if y==2030:
                scenario_rows[case]=r
                br=b.row('Driver bridge',[case,None,None,None,None,None,None,None,'Supply increases reduce imports; Mozambique is route diversion only and does not reduce national demand or imports'])
                for c,f in [('B',activity),('C',efficiency),('D',rail),('E',powerchange),('F',operating),('G',restart),('H',f'B{br}+C{br}+D{br}+E{br}-F{br}-G{br}')]:b.fx('Driver bridge',br,c,f)
                bridges[case]=br
    # Source-scoped node inventory, never summed into a corridor capacity.
    nodes={}
    for node,vol,unit,status,url in payload['nodes']:
        r=b.row('Mozambique',[node,vol,unit,status+'; '+url]);nodes[node]=r
    for y in range(2019,2026):
        r=b.row('Mozambique',[f'Komatipoort imports {y}',None,'bn L','SARS office proxy; not terminal-specific; litres only'])
        b.fx('Mozambique',r,'B',f'{e[f"trade_Komatipoort_import_petrol_{y}"]}+{e[f"trade_Komatipoort_import_diesel_{y}"]}')
    def moz(label,formula,unit,note):
        r=b.row('Mozambique',[label,None,unit,note]);return b.fx('Mozambique',r,'B',formula)
    rate=a['truck_cost_zar_km'];load=a['truck_payload_litres']
    durban=moz('Durban road logistics',f'2*{a["road_distance_durban_km"]}*{rate}/{load}+{a["terminal_cost_durban_zar_l"]}','ZAR/L','Illustrative same inland destination; round-trip truck cost includes empty return; excludes common product price and taxes')
    matola=moz('Matola road logistics',f'2*{a["road_distance_matola_km"]}*{rate}/{load}+{a["terminal_cost_matola_zar_l"]}+{a["border_cost_matola_zar_l"]}+{a["border_delay_days"]}*{a["truck_delay_zar_day"]}/{load}+{a["inventory_price_zar_l"]}*{a["financing_rate"]}*{a["border_delay_days"]}/365+{a["matola_landed_premium_zar_l"]}','ZAR/L','Illustrative costs, not freight quotes. Landed product premium is editable; comparable tax treatment assumed, not a legal assessment')
    moz('Matola premium vs Durban',f'{matola}-{durban}','ZAR/L','Positive value means Matola is more expensive under these assumptions')
    moz('Required Matola landed discount',f'MAX(0,{matola}-{durban})','ZAR/L','Discount required to offset the modelled logistics disadvantage')
    galp=moz('Galp SA volume screen',f'{b.ref("Mozambique",nodes["Galp/IPG Matola"])}*{a["galp_working_fraction"]}*{a["galp_monthly_turns"]}*12*{a["galp_sa_allocation"]}/1000000','bn L/year','Individual facility sensitivity only; no customer commitment. Not additive to Petromoc pending asset overlap check')
    petromoc=moz('Petromoc SA volume screen',f'{b.ref("Mozambique",nodes["Petromoc Lingamo"])}*{a["petromoc_pd_fraction"]}*{a["petromoc_working_fraction"]}*{a["petromoc_monthly_turns"]}*12*{a["petromoc_sa_allocation"]}/1000000','bn L/year','Individual facility sensitivity; assumed petrol/diesel share, working capacity and SA allocation. Not added to Galp')
    for label,key in [('Low','border_delay_low_days'),('Base','border_delay_days'),('High','border_delay_high_days')]:
        moz(f'Matola premium: {label} border delay',f'{matola}-{durban}+({a[key]}-{a["border_delay_days"]})*({a["truck_delay_zar_day"]}/{load}+{a["inventory_price_zar_l"]}*{a["financing_rate"]}/365)','ZAR/L','Delay sensitivity; see editable days in Assumptions; all other route inputs fixed')
    for case,v in case_refs.items():
        moz(f'Trucks/day: {case} diversion',f'{v["moz_diversion_bn"]}*1000000000/{load}/{a["operating_days"]}','loaded trucks/day','Incremental SA flow scenario; compare with terminal loading and border availability, not gross port capacity')
    for label,ref,unit,note in [
        ('2025 demand estimate',D,'bn L','Department 2023 sales extended with explicit activity, efficiency and power assumptions'),
        ('2025 FIASA-anchor sensitivity',b.ref('Demand history',alt25,'D'),'bn L','Alternative 2024 source followed by the same annual drivers'),
        ('2025 domestic production',S,'bn L','User-directed planning assumption; plant estimate retained separately' if planning_case else 'Petrol/diesel subset estimated from plant output'),
        ('2025 gross customs imports',I,'bn L','Recorded national trade, not a demand estimate'),
        ('Unexplained supply-demand difference',b.ref('Balance',gap,'D'),'bn L','Keep visible; do not present a fully reconciled national balance'),
        ('2030 base demand',b.ref('Scenarios',scenario_rows['Base'],'B'),'bn L','Explicit scenario, not reported forecast'),
        ('2030 base import change',b.ref('Scenarios',scenario_rows['Base'],'E'),'bn L','Change is more interpretable than the unresolved absolute import level'),
        ('2030 base trade-anchored imports',b.ref('Scenarios',scenario_rows['Base'],'F'),'bn L','2025 customs plus modelled change; holds unexplained difference constant'),
        ('2030 base Mozambique diversion',b.ref('Scenarios',scenario_rows['Base'],'G'),'bn L','Route substitution; does not reduce national imports'),
        ('Matola logistics premium',f'{matola}-{durban}','ZAR/L','Assumed route economics; obtain comparable quotes'),
    ]:
        r=b.row('Summary',[label,None,unit,note]);b.fx('Summary',r,'B',ref)
    # Normalise exponent syntax only at export, preserving numeric graph values.
    for sheet in b.sheets.values():
        for row in sheet['rows']:
            for cell in row:
                if isinstance(cell,dict):cell['formula']=cell['formula'].replace('**','^')
    return {'sheets':b.sheets,'summary':{row[0]:row[1]['value'] for row in b.sheets['Summary']['rows']},'status':'Directed 5.8bn national supply case; aggregate and product balances shown separately' if planning_case else 'Analyst base case and sensitivities; independent demand and supply do not yet reconcile'}
