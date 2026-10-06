"""Order the partner story and expose evidence gaps without inventing observations."""
import json
import re
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_CONNECTOR


def structure_scr(prs, slide, text, root, brand):
    original = list(prs.slides)
    register = json.loads((root/'story/partner_story_gap_register_2026_10_06.json').read_text(encoding='utf-8'))
    by_id = {r['id']: dict(r) for r in register['rows']}
    references = {2:3,3:4,4:6,5:9,6:11,7:12,8:14}
    for r in by_id.values():
        r['existing_work'] = re.sub(r'\bp([2-8])\b', lambda m: 'p'+str(references[int(m[1])]), r['existing_work']).replace('pp2-3,7','pp3-4,12')
    groups = [
        ('Reconcile domestic supply and finished imports', 'Situation | national balance and import entry ports', ['SA03','SA04']),
        ('Translate demand drivers into explicit fuel levers', 'Complication | power, freight, fleet and economic activity', ['SA05','SA06','SA07','SA08']),
        ('Test refinery availability and plant-specific scenarios', 'Complication | refinery closures, restart proposals and Sasol / Natref', ['SA09','SA10']),
        ('Compare routes on the same delivered-cost basis', 'Complication | Durban-NMPP-Lesedi, road / rail, Matola and Walvis Bay', ['SA11']),
        ('Establish actual share and additional contestable demand', 'Resolution | unique deliveries, reachable customers and commercial access', ['SA12','SA13']),
        ('Gate investment on evidenced incremental customer flows', 'Resolution | optional service and investment assessment', ['SA14']),
    ]
    added = []
    for title, heading, ids in groups:
        rows = [by_id[i] for i in ids]
        s = slide(title, 'Partner SA storyboard; open evidence register, 6 Oct 2026. Placeholder; no forecast or actual share inferred.',
                  json.dumps(rows, indent=2))
        added.append(s)
        text(s, heading, .5, 1.78, 7.05, .55, 14, True)
        text(s, 'EVIDENCE GAP | analysis specification, not a populated result', .5, 2.35, 7.05, .30, 11, True, brand.accent_primary)
        spacing = 1.02 if len(rows)==4 else 1.77
        for i, r in enumerate(rows):
            y = 2.88+i*spacing
            text(s, r['question'], .5, y, 7.05, .32, 14, True, brand.accent_primary)
            copy = (r['gap']+'\nOutput: '+r['closure_evidence']) if len(rows)<4 else r['closure_evidence']
            text(s, copy, .5, y+.37, 7.05, .92 if len(rows)<4 else .61, 12)
        if len(rows)==1:
            text(s, 'Evidence required before quantification', .5, 4.68, 7.05, .32, 14, True, brand.accent_primary)
            text(s, rows[0]['existing_work']+'\n'+rows[0]['model_connection'], .5, 5.10, 7.05, 1.10, 12)
        next_step = 'Manish: assemble the stated evidence and document source, vintage and consuming calculation. Nigel reviews the scenario or commercial conditions. Detailed actions and closure tests are in the slide notes.'
        if ids==['SA03','SA04']:
            next_step = 'Manish: reconcile the national fuel balance, then bridge finished imports to entry ports. Nigel: secure source access. Explain all unit conversions and unallocated volumes.'
        elif ids==['SA09','SA10']:
            next_step = 'Manish: resolve duplicate refinery keys and source plant status. Henry: review the gas/liquid mechanism. Nigel: agree conditional refinery scenarios.'
        elif ids==['SA11']:
            next_step = 'Nigel: choose the first product and customer destination. Manish: compare dated route costs, capacity and access on the same R/litre basis. Henry reviews.'
        elif ids==['SA12','SA13']:
            next_step = 'Nigel: request client flow and destination records. Manish: reconcile transfers, calculate unique served demand, then test additional customer access and competing storage.'
        elif ids==['SA14']:
            next_step = 'Nigel: decide whether to prioritise investment analysis after the flow case. Manish and Henry: bridge incremental flows to usable stock and service constraints.'
        # Four-driver page needs a concise action list; full actions remain in notes/register.
        if len(rows)==4:
            next_step = 'Manish: define baseline, alternatives, units, dates and consuming equation for each lever. Nigel reviews; calibrate against source observations.'
        findings = [('Evidence status', 'These topics remain open. Existing calculations or public source leads do not establish calibration or closure.'),
                    ('What is already available', rows[0]['existing_work']),
                    ('What this page will resolve', 'A traceable petrol/diesel result with source, period, units and explicit unassessed residual. Jet stays separate.')]
        panel(s, text, brand, findings, next_step)
    # Findings and actions occupy visibly separate parts of the right-hand panel.
    specs = {
        1: ([('Demand is concentrated', 'Gauteng, KwaZulu-Natal and Western Cape account for 68.6% of reported 2022 petrol/diesel sales.'),('Regions are working groups', 'Province boundaries define reporting groups; they do not establish terminal catchments.'),('Sales are historical demand evidence', 'The map is sourced provincial sales, rather than a current-year outlook or commercial accessibility result.')], 'Manish: source a later complete year and test actual destinations, route costs and customer access.'),
        2: ([('History ends in 2022', 'The latest complete provincial year in this extract is 2022.'),('2023 is incomplete', 'Only Q1 is present; it is excluded from annual comparisons.'),('Six years are flagged', 'Provincial sums differ from national sales in 2013, 2014, 2015, 2017, 2018 and 2021.')], 'Manish: reconcile each flagged value to its original workbook cell and log old value, proposed value and reason.'),
        3: ([('Demand totals are sourced', 'The provincial bars use reported 2022 petrol/diesel sales.'),('Origin shares are illustrative', 'Domestic/import fractions are authored examples; no actual provincial origin allocation is established.'),('Imports need a national balance', 'Exports and stock movements must be reconciled before a sourced import requirement can be presented.')], 'Manish: populate the matched-year national balance first; retain provincial origin as unknown until supported.'),
        4: ([('Darker cells mean lower example cost', 'The surface shows illustrative delivered road-transport cost in R/litre.'),('Other modes remain context', 'Pipeline and rail costs, capacity and access are not evaluated in this surface.'),('Physical proximity is insufficient', 'No operational or commercial catchment is validated by this illustration.')], 'Manish and Nigel: select the first destination and obtain dated route tariffs, quotations and access evidence.'),
        5: ([('Balance arithmetic is illustrative', 'Example demand 21.0 less domestic production 7.0 gives imports 14.0, before exports and stocks.'),('Transfers count once', 'Example Durban receipts 2.8 plus Lesedi receipts 2.0 less shared transfer 1.8 gives unique served demand 3.0.'),('Candidate volume is conditional', 'The example envelope is 8.5 and additional candidate volume 5.5; neither is forecast capture.')], 'Nigel: request client flows. Manish: replace examples with matched-year product and destination records.'),
        7: ([('Capacity is a stock', 'Published tank volumes are not annual fuel deliveries or market share.'),('The inventory is partial', 'Missing capacities are unknown, rather than zero; mixed product scopes limit comparison.'),('Leases are conditional', 'Transnet lease tanks are not counted as currently available operating supply.')], 'Manish: verify product compatibility, capacity basis and operating status. Nigel: confirm usable client capacity.'),
    }
    for i, (findings, action) in specs.items():
        panel(original[i], text, brand, findings, action)
    # Competitor detail is retained as a dedicated regional inventory, not labelled findings.
    for q in original[6].shapes:
        if q.has_text_frame and q.text.startswith('Key takeaways'):
            q.text_frame.paragraphs[0].runs[0].text = 'Regional competitor evidence'
    # SCR overview is the first analytical page; page references are generated below.
    panel(original[8], text, brand, [('Situation', 'Establish demand, domestic output and finished imports; locate the economically reachable market.'),('Complication', 'Test demand-driver reversals, refinery cases and the relative cost and feasibility of competing routes.'),('Resolution', 'Establish actual Vopak share and additional contestable customer flows. Investment follows the flow case.')], 'Manish: close baseline/source flags and define levers. Nigel: obtain client flows and choose the first corridor. Week windows remain proposed.')
    for q in original[8].shapes:
        if q.has_text_frame:
            for p in q.text_frame.paragraphs:
                for run in p.runs:
                    run.text = run.text.replace('(pp.2-3,7-8)', '(pp.3-4,12,14)')
    ordered = [original[0],original[8],original[1],original[2],added[0],original[3],added[1],added[2],original[4],added[3],original[5],original[6],added[4],original[7],added[5],original[9]]
    sid_by_slide = {s.part: sid for s,sid in zip(prs.slides,list(prs.slides._sldIdLst))}
    for sid in list(prs.slides._sldIdLst): prs.slides._sldIdLst.remove(sid)
    for s in ordered: prs.slides._sldIdLst.append(sid_by_slide[s.part])
    for i,s in enumerate(prs.slides,1):
        for q in s.shapes:
            if q.has_text_frame:
                for paragraph in q.text_frame.paragraphs:
                    for run in paragraph.runs:
                        run.text = run.text.replace('operator sources on slide 7', 'operator sources on slide 12').replace('site inventory in slide 2 notes', 'site inventory in slide 3 notes')
        s.notes_slide.notes_text_frame.text += f'\nSCR delivery order: page {i} of 16. Gap IDs and original evidence references retained in notes.'

    from scr_summary_table import apply_summary
    apply_summary(prs,text,brand)
    from scr_navigation import apply_navigation
    apply_navigation(prs,brand)


def panel(s, text, brand, findings, action):
    for q in list(s.shapes):
        if q.has_text_frame and q.left>=Inches(8.0) and Inches(1.7)<=q.top<Inches(6.9):
            q._element.getparent().remove(q._element)
    text(s,'Evidence and implications',8.12,1.78,4.03,.34,18,True)
    for i,(heading,body) in enumerate(findings):
        y=2.39+i*1.05
        text(s,f'{i+1:02d} | {heading}',8.12,y,4.03,.40,14,True,brand.accent_primary)
        text(s,body,8.12,y+.42,4.03,.63,12.5)
    q=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(8.12),Inches(5.65),Inches(12.15),Inches(5.65))
    q.line.color.rgb=brand.accent_primary;q.line.width=Pt(.8)
    text(s,'Next steps | proposed owners',8.12,5.82,4.03,.32,14,True,brand.accent_primary)
    text(s,action,8.12,6.22,4.03,.68,11.5)
