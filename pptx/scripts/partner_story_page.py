"""Partner SCR story with open evidence and explicit closure actions."""
import json
from pptx.util import Inches,Pt
from pptx.enum.shapes import MSO_CONNECTOR


def add_partner_story_page(slide,exhibit_layout,text,root,brand):
    path=root/'story/partner_story_gap_register_2026_10_06.json'
    register=json.loads(path.read_text(encoding='utf-8'))
    assert len(register['rows'])==14
    notes=('Partner storyboard pp30-32 supplied in chat and preserved under external/partner_story_20261006/. '
           'Partner propositions are hypotheses, not assertions that reversals or refinery projects have occurred. '
           'All gap records are open pending the stated evidence and review. Work windows/owners are planning targets. '
           'Fuel-model integration takes precedence over broad infrastructure or detailed service sizing. '
           'Jet remains separately tracked and excluded from client petrol/diesel totals. '
           'Detailed analyst review: workstreams/WS3_reporting_delivery/partner_story_alignment_2026-10-06.md.\n'
           +json.dumps(register,indent=2))
    s=slide('Connect the SA market story to evidence and next actions',
            'Partner SA storyboard pp.30-32; repository evidence and diagnostics, 6 Oct 2026. All gaps remain open.',notes)
    exhibit_layout(s,'Situation - Complication - Resolution | evidence and gaps',[
        ('Baseline before forecasts','Manish: reconcile flagged rows; map each used/staged input to its calculation and affected output. Nigel reviews.'),
        ('Define levers in Week 1','Rail, BEV/hybrid, efficiency, power dispatch and refinery cases need baseline, alternatives, units, dates and equations.'),
        ('Request actual Vopak flows','Nigel requests receipts, transfers, deliveries and destinations. Manish reconciles unique demand; actual share stays unknown.'),
        ('Compare the competing routes','Durban-NMPP-Lesedi versus Durban road/rail, Matola and Walvis Bay: same product, destination and cost basis.'),
    ])
    rows=[
        (2.40,'01 Situation | establish the market baseline',
         'Have: demand history, regions and operators (pp.2-3,7-8).\nGap: recent fuel balance, finished imports and entry ports.\nClose: matched-year balance and exact data reconciliation. W1-W2.'),
        (3.82,'02 Complication | quantify what could change',
         'Have: provisional vehicle, power-diesel and supply calculations.\nGap: calibrated driver reversals, refinery cases and route costs.\nClose: define levers in W1; test their litres/import effects in W2-W4.'),
        (5.24,'03 Resolution | establish Vopak opportunity',
         'Have: regional competitor footprint and published tank stocks.\nGap: actual share, customer access and additional contestable volume.\nClose: client flows + cost/access tests; investment follows the flow case.'),
    ]
    for y,heading,body in rows:
        text(s,heading,.5,y,7.05,.31,14,True,brand.accent_primary)
        text(s,body,.5,y+.43,7.05,.86,11.5)
        q=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(.5),Inches(y+1.30),Inches(7.55),Inches(y+1.30))
        q.line.color.rgb=brand.grey_fill;q.line.width=Pt(.5)
    text(s,'Week windows are targets. Partner propositions require testing; they are not established findings.',.5,6.88,7.05,.23,9)
    return s
