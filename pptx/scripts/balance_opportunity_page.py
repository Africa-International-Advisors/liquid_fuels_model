"""Explain the analytical bridge from fuel balance to terminal service needs."""
from pptx.util import Inches, Pt


def draw_balance_opportunity(slide,text,table):
    text(slide,'Purpose: connect the national fuel outlook to evidence of demand for Vopak services',.55,1.8,11.5,.4,15)
    rows=[
        '| Step | Question to resolve | Output for the next step |',
        '| 01 National balance | How much fuel must be imported after domestic production, exports and stock movements? | Import requirement by fuel and period; compare with available supply to identify the unmet gap |',
        '| 02 Feasible flows | Which ports and inland routes can actually deliver the available volumes? | Feasible flows and bottlenecks after transport, power and terminal-capacity constraints |',
        '| 03 Commercial access | Which customer flows could Vopak serve, given contracts, competitors and access? | Customer volumes accessible to Vopak; assumptions and evidence gaps remain explicit |',
        '| 04 Service needs | What receipt, handling, dispatch and inventory needs follow from those flows? | Terminal throughput, handling needs and usable storage; implications for existing assets and growth |',
    ]
    shape=table(slide,rows,y=2.5,height=3.83,widths=[2.15,4.75,4.75],size=15)
    for row in shape.table.rows:
        for cell in row.cells:
            cell.margin_top=cell.margin_bottom=Inches(.04)
            for p in cell.text_frame.paragraphs:
                p.space_after=Pt(0);p.line_spacing=1.0
    text(slide,'Each step needs evidence: required imports are not guaranteed delivery. Throughput is a flow; storage is a stock.',.55,6.65,11.5,.4,12,True)
