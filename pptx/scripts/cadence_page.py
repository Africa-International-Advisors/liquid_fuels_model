"""Proposed engagement cadence; does not create calendar commitments."""
from pptx.util import Inches, Pt


def draw_cadence(slide,text,table):
    text(slide,'Proposed working rhythm | Monday HG check-in already planned; recurring slots and client dates to agree',.55,1.8,11.5,.5,14)
    rows=[
        '| Touchpoint | Frequency and participants | Required output |',
        '| Internal check-in | Daily, 10–15 minutes; Manish + Nigel | Today’s priorities, expected outputs, dependencies and blockers |',
        '| Internal check-out | Daily written update; Manish to Nigel; call if blocked | Completed work and evidence links; checks, changes, open gaps and next steps |',
        '| Technical review | Weekly and at model gates; Manish + Nigel; Henry at gates | Reconciled baseline, assumptions, calculation checks and integration evidence; review findings recorded |',
        '| Partner review | Weekly proposed slot, before client checkpoints; partner + Nigel; Manish supports | Partner-led SCR and storyline; technical evidence, emerging implications, gaps and decisions needed |',
        '| Client touchpoints | Proposed weeks 1, 3, 5 and 6; partner leads, model team as needed | W1: scope/data; W3: emerging findings; W5: draft implications; W6: final review and handover |',
    ]
    shape=table(slide,rows,y=2.45,height=3.95,widths=[2.05,3.55,6.05],size=14)
    for row in shape.table.rows:
        for cell in row.cells:
            cell.margin_top=cell.margin_bottom=Inches(.045)
            for p in cell.text_frame.paragraphs:
                p.space_after=Pt(0);p.line_spacing=1.0
    text(slide,'Monday HG check-in: align the technical workstream, responsibilities and ways of working before delivery proceeds.',.55,6.65,11.5,.4,12,True)
