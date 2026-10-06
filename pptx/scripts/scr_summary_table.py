"""Native summary table and bidirectional SCR page references."""
from pptx.util import Inches, Pt
from pptx.enum.text import MSO_ANCHOR
from pptx.oxml.xmlchemy import OxmlElement
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from brand_pptx import _strip_table_style, cell_bottom_rule
from brand_configs import vopak as cfg


ROWS = [
    ('S1\nSituation', 'Demand baseline and regional market\nHave: provincial sales history and map. Reconcile six flagged years; refresh a complete year.',
     'Manish\nNigel review', 'W1–W2\nSourced demand baseline', [3,4]),
    ('S2\nSituation', 'Domestic supply, finished imports and entry ports\nHave: 2024 sales/trade; diesel imports conflict. Gap: matched output/stocks and product-specific port allocation.',
     'Manish\nNigel access', 'W1–W3\nFuel balance + port bridge', [5,6]),
    ('C1\nComplication', 'Demand drivers and levers\nHave: indexed power, road/rail, BEV/hybrid sales and real GDP. Refresh prices; calibrate baseline/alternatives into litres effects.',
     'Manish\nNigel review', 'W1 define; W2–W4 test\nLever-to-demand bridge', [7]),
    ('C2\nComplication', 'Refinery and plant scenarios\nHave: published capacity history and conditional CEF case. Agree timing/yields; resolve repeated keys and plant mechanisms.',
     'Manish\nHenry / Nigel', 'W1–W3\nPlant output + imports', [8]),
    ('C3\nComplication', 'Economic accessibility and competing routes\nCost map is illustrative. Compare Durban–NMPP–Lesedi, road/rail, Matola and Walvis Bay for the same product and destination.',
     'Manish\nNigel / Henry', 'W1 scope; W2–W4 test\nDelivered R/litre + access', [9,10]),
    ('R1\nResolution', 'Actual Vopak share and contestable customer demand\nShare is unknown. Test each candidate increment against cost, physical capacity, commercial rights and unique deliveries.',
     'Nigel client data\nManish analysis', 'W1 request; W2–W4 test\nServed + contestable litres', [11,12,13]),
    ('R2\nResolution', 'Storage and optional investment\nPartial published stocks are available. Verify usable product capacity; size additional service needs only after the incremental flow case.',
     'Nigel priority\nManish / Henry', 'W4–W6 if prioritised\nFlow-to-stock / investment', [14,15]),
]


def apply_summary(prs, text, brand):
    overview = prs.slides[1]
    for q in list(overview.shapes):
        if Inches(1.7)<=q.top<Inches(7.05):
            q._element.getparent().remove(q._element)
    for q in overview.shapes:
        if q.has_text_frame and q.text.startswith('Connect the SA market story'):
            q.text_frame.paragraphs[0].runs[0].text = 'Resolve the SA fuel outlook, then test Vopak’s accessible market'
    text(overview, 'Situation → Complication → Resolution | evidence, actions and delivery roadmap',
         .5, 1.78, 11.65, .30, 14, True, brand.accent_primary)
    widths = [1.02,5.03,1.65,2.72,1.23]
    shape = overview.shapes.add_table(8,5,Inches(.5),Inches(2.22),Inches(sum(widths)),Inches(4.42))
    shape.name = 'SCR master roadmap | native PowerPoint table'
    t = shape.table
    _strip_table_style(t)
    for col,w in zip(t.columns,widths): col.width=Inches(w)
    headers = ['SCR reference','Evidence and required next step','Proposed lead','Timing and output','Deep dives']
    t.rows[0].height = Inches(.40)
    for r in list(t.rows)[1:]: r.height=Inches(.574)
    for i,row in enumerate([headers]+[[a,b,c,d,' / '.join(str(p) for p in pages)] for a,b,c,d,pages in ROWS]):
        for j,value in enumerate(row):
            cell=t.cell(i,j);cell.text=value
            cell.margin_left=cell.margin_right=Inches(.05)
            cell.margin_top=Inches(.055);cell.margin_bottom=Inches(.02)
            cell.vertical_anchor=MSO_ANCHOR.TOP
            cell.fill.solid();cell.fill.fore_color.rgb=brand.white
            for p in cell.text_frame.paragraphs:
                p.font.name=cfg.THEME_FONT;p.font.size=Pt(10.5 if j in (1,3) else 10)
                p.font.bold=i==0 or j==0
                p.font.color.rgb=brand.accent_primary if j in (0,4) else brand.ink
                p.space_after=Pt(0)
            cell_bottom_rule(cell, color=brand.grey_fill, w_pt=0.6)
            if i and j==4:
                pages=ROWS[i-1][4]
                p=cell.text_frame.paragraphs[0];p.clear()
                for k,page in enumerate(pages):
                    run=p.add_run();run.text=(' / ' if k else '')+str(page)
                    run.font.name=cfg.THEME_FONT;run.font.size=Pt(11);run.font.color.rgb=brand.accent_primary
                    link=OxmlElement('a:hlinkClick')
                    link.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id',
                             overview.part.relate_to(prs.slides[page-1].part,RT.SLIDE))
                    link.set('action','ppaction://hlinksldjump')
                    run._r.get_or_add_rPr().append(link)
    text(overview, 'Petrol + diesel; jet separate. Owners and weeks are proposed. Open gaps and illustrations remain explicitly labelled.',
         .5,6.85,11.65,.25,10)
    mapping={page:(ref.split('\n')[0],ref.split('\n')[1]) for ref,_,_,_,pages in ROWS for page in pages}
    for page,(ref,stage) in mapping.items():
        s=prs.slides[page-1]
        for old in list(s.shapes):
            if old.name.startswith('SCR backlink'):
                old._element.getparent().remove(old._element)
        q=text(s,f'SCR {ref} | {stage} | Return to overview: page 2',.5,.61,11.65,.24,10.5,True,brand.accent_primary)
        q.name=f'SCR backlink {ref}'
        q.click_action.target_slide=overview
        s.notes_slide.notes_text_frame.text+=f'\nSCR master row {ref}; linked roadmap page 2. Deep-dive page {page}.'
    overview.notes_slide.notes_text_frame.text+='\nMaster SCR rows: '+str(ROWS)+'\nSlide links connect each roadmap row to its deep dives, with backlinks to page 2.'
