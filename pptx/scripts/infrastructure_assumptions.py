"""Required infrastructure assumptions, with transport and power units separated."""


def draw_infrastructure_assumptions(slide,text,table):
    text(slide,'Required inputs by asset class | sourced assumptions to build, not validated capacities',.55,1.82,11.5,.36,16,True)
    rows=[
        '| Asset class | Required assumptions | Model connection |',
        '| Ports | Berths, vessel / parcel limits, discharge rates, operating windows and terminal connections | Import receipts and export dispatch |',
        '| Airports | Jet demand allocation, supply routes, tankage, hydrant / receipt limits and stock cover | Aviation fuel delivery and inventory |',
        '| Rail | Fuel-compatible links, train paths, wagons, payload, turnaround and service reliability | Feasible rail fuel throughput |',
        '| Roads | Routes, tanker payloads, fleet availability, trip times, access and operating restrictions | Feasible road fuel throughput |',
        '| Pipelines | Product / gas type, direction, links, throughput, availability and shared capacity | Liquid-fuel flows; gas dependencies separate |',
        '| Power lines | Grid connections, transfer limits, outages and supply reliability at relevant assets | Constraints on asset operations and backup demand |',
        '| Power stations | Fuel / technology, MW, commissioning, availability, dispatch and efficiency | Fuel demand and electricity supply context |',
        '| Tanks / storage | Gross vs working capacity, segregation, commitments, stock cover and handling limits | Usable inventory and handling constraints |',
    ]
    shape=table(slide,rows,x=.55,y=2.38,height=3.95,widths=[1.72,6.02,3.91],size=13)
    from pptx.util import Inches, Pt
    for row in shape.table.rows:
        row.height=Inches(3.95/len(shape.table.rows))
        for cell in row.cells:
            cell.margin_top=cell.margin_bottom=Inches(.025)
            for paragraph in cell.text_frame.paragraphs:
                paragraph.space_before=paragraph.space_after=Pt(0)
                paragraph.line_spacing=1.0
                paragraph.font.size=Pt(12)
    text(slide,'Use source, vintage, units, owner and access basis for every input. Missing capacity remains unknown.',.55,6.5,11.5,.32,13,True)
    text(slide,'Fuel transport: m3/year | Storage: m3 | Electricity: MW / MWh. Do not convert power-line capacity directly into fuel throughput.',.55,6.85,11.5,.22,10)
