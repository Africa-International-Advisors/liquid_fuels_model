"""Evidence and model-reference pages for the PDF review."""
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR


def compact(shape):
    for row in shape.table.rows:
        for cell in row.cells:
            cell.margin_top=cell.margin_bottom=Inches(.025)
            for p in cell.text_frame.paragraphs:
                p.space_after=Pt(0);p.line_spacing=1.0


def draw_inventory(slide,text,table):
    text(slide,'Active vintage: 2026 draft | module-level inventory; full declarations remain in the input register',.55,1.8,11.5,.35,15)
    rows=['| Module / fuel | Assumptions used | H/L treatment | Evidence / status |',
      '| Vehicles / petrol, diesel | GDP per capita; sales regression; EV uptake; fleet cohorts; scrappage; mileage; fuel and segment mix; efficiency | GDP, EV and efficiency vary; other parameters shared | Workbook regression / EV inputs dated 24 Mar 2025. Fleet/activity parameters provisional; opening stock unresolved. |',
      '| Aviation / jet | GDP per capita; departing passengers; regression coefficients; jet allocation; declared monthly profile | GDP varies; passengers and coefficients shared | Workbook RegJetFuel / PaxBaseScenario, 24 Mar 2025. Departures are the current proxy; arrivals, cargo and flight movements are not separately modelled. Validate fuel coverage; monthly profile not wired. |',
      '| Power / diesel | OCGT MW; load factor; efficiency; energy per litre; operating days; commissioning coverage | Load factor varies; capacity and conversions shared | Workbook named ranges, 24 Mar 2025. Dispatch and commissioning need validation; load-shedding series not wired. |',
      '| Industry / diesel | Base-year volume; GDP scaling; elasticity; declared product / monthly allocation | Baseline / elasticity shared; macro path varies | Provisional baseline and elasticity; no verified inventory/date; declared monthly profile not wired. |',
      '| Agriculture / diesel | Base-year volume; GDP scaling; elasticity; product allocation | Baseline / elasticity shared; macro path varies | Provisional placeholders; hectares/activity driver still to build. |',
      '| Marine / diesel, fuel oil | Base-year volume; GDP scaling; elasticity; product split | Baseline / split shared; macro path varies | Provisional baseline and split; port/bunker evidence still needed. Fuel oil shown separately. |']
    compact(table(slide,rows,y=2.12,height=4.18,widths=[1.65,4.05,2.1,3.85],size=11))
    text(slide,'Full values: companion Assumption Inventory PDF. All six modules require review; M is unset.',.55,6.85,11.5,.2,10,True)


def draw_excel(slide,text,table,brand):
    text(slide,'Inherited workbook | sheet-level calculation and reporting structure',.55,1.8,11.5,.35,16)
    nodes=[('01 Inputs & fits','Assumptions\nRegGasoline / RegDiesel\nRegJetFuel / RegEV\nPassenger data sheets'),
           ('02 Forecasts','fGasoline / fDiesel\nfJetFuel / fEV Penetration\nSupply Forecast'),
           ('03 Balances & imports','Fuel DemandSupply sheets\nTotal LF - DemandSupply\nfImports\nRegional allocations'),
           ('04 Storage & client use','Deficit Calculations\nMarket share\nSummary\nStorage / throughput views')]
    for i,(title,body) in enumerate(nodes):
        x=.55+i*2.98
        box=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(2.65),Inches(2.7),Inches(2.35))
        box.fill.background();box.line.color.rgb=brand.grey_fill
        text(slide,title,x+.1,2.8,2.5,.45,14,True)
        text(slide,body,x+.1,3.4,2.5,1.5,12)
        if i<3:
            arrow=slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,Inches(x+2.72),Inches(3.65),Inches(.24),Inches(.2))
            arrow.fill.solid();arrow.fill.fore_color.rgb=brand.accent_primary;arrow.line.fill.background()
    text(slide,'Scenario logic and limitations',.55,5.35,11.5,.3,17,True)
    text(slide,'High/low demand and production assumptions feed workbook formulas; this is not yet the independent nine-case H/M/L matrix.',.55,5.85,11.5,.5,15)
    text(slide,'fImports contains external workbook references. Cached values, regional allocation formulas and storage/market-share assumptions need reconciliation.',.55,6.45,11.5,.5,13)


def draw_bridges(slide,text,brand,data):
    text(slide,'2024 | Python minus Excel recorded demand | billion litres | accounting bridges, not causal attribution',.55,1.8,11.5,.4,14)
    details={
      'petrol':('Petrol',[],'Reconcile fleet coverage, mileage and fuel economy. The two effects offset each other.'),
      'diesel':('Diesel',[], 'Power basis and provisional sector volumes drive the gap. Road vs non-power is not like-for-like; check overlap.'),
      'jet':('Jet',[], 'Python matches Excel calculated demand. The gap is between the regression and recorded demand, not the translation.')}
    for i,key in enumerate(['petrol','diesel','jet']):
        r=data[key];x=.55+i*4.0;label,_,note=details[key]
        text(slide,label,x,2.4,3.7,.3,19,True)
        text(slide,f'Net gap: {(r["python"]-r["observed"])/1e9:+.2f}',x,2.83,3.7,.3,16,True)
        effects=list(r['effects'].items());limit=max(abs(v) for _,v in effects)/1e9 or 1
        for j,(name,value) in enumerate(effects):
            y=3.35+j*.53
            text(slide,name,x,y,3.7,.22,10)
            centre=x+1.85;v=value/1e9;length=abs(v)/limit*1.3
            zero=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(centre),Inches(y+.23),Inches(centre),Inches(y+.44));zero.line.color.rgb=brand.ink;zero.line.width=Pt(.4)
            if length>.001:
                bar=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(centre-length if v<0 else centre),Inches(y+.27),Inches(length),Inches(.12));bar.fill.solid();bar.fill.fore_color.rgb=brand.accent_primary;bar.line.fill.background()
            text(slide,f'{v:+.2f}',x+3.15,y+.23,.65,.22,10)
        text(slide,note,x,5.78,3.65,.86,12)
    text(slide,'Each panel uses its own scale. Petrol and diesel sector/stock assumptions remain provisional; jet fuel definitions need review.',.55,6.8,11.5,.23,10)
