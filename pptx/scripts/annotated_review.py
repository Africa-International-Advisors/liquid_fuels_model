"""Apply Nigel's approved 7 October editorial structure to the native deck.

Consumes existing evidence and copy. Does not execute or duplicate the fuel model.
"""
import json
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from brand_pptx import BrandStyle, next_version_path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from brand_configs import vopak as cfg
from convergence_feedback import text, replace
from convergence_story_order import native_table
from agenda_answer_page import _links


def title(slide, value):
    replace(next(q for q in slide.shapes if q.name == 'Title 1'), value)


def remove(shape):
    shape._element.getparent().remove(shape._element)


def clear(slide, right=False):
    for q in list(slide.shapes):
        if Inches(1.7) <= q.top < Inches(7.04) and (not right or q.left >= Inches(8)):
            remove(q)


def right_panel(slide, sections, brand, action=None):
    clear(slide, right=True)
    text(slide, 'Implication for Vopak', 8.12, 1.78, 4.03, .34, 17, True, brand.ink)
    for i, (heading, body) in enumerate(sections):
        y = 2.40 + i * 1.14
        text(slide, heading, 8.12, y, 4.03, .34, 12.5, True, brand.ink)
        text(slide, body, 8.12, y + .38, 4.03, .73, 11.5, color=brand.ink)
    if action:
        text(slide, action[0], 8.12, 5.94, 4.03, .28, 12.5, True, brand.ink)
        text(slide, action[1], 8.12, 6.30, 4.03, .60, 11.5, color=brand.ink)


def apply_annotated_review(prs, root, brand):
    spec = json.loads((root / 'story/annotated_revision_2026_10_07.json').read_text(encoding='utf-8'))
    entries = {p['page']: p for p in spec['pages'] if 'page' in p}
    original = list(prs.slides)
    assert len(original) == 31, 'Expected the reviewed 31-page candidate'
    s = lambda n: original[n - 1]

    # Cover margins follow the existing title edge.
    for q in s(1).shapes:
        if q.has_text_frame and q.name == 'Strictly Confidential footer':
            q.left = Inches(.65)

    # Existing overview table and slide links remain native.
    title(s(3), entries[3]['title'])
    table = next(q.table for q in s(3).shapes if q.has_table)
    table.cell(0, 2).text = 'Finding'
    table.cell(0, 3).text = 'Implication for Vopak'
    for c in (2, 3):
        for p in table.cell(0,c).text_frame.paragraphs:
            p.font.name=cfg.THEME_FONT;p.font.size=Pt(10.5);p.font.bold=True;p.font.color.rgb=brand.ink
    for i, row in enumerate(entries[3]['rows'], 1):
        for c, value in [(2, row[2]), (3, row[3])]:
            cell = table.cell(i, c)
            cell.text = value
            for p in cell.text_frame.paragraphs:
                p.font.name = cfg.THEME_FONT
                p.font.size = Pt(10.5)
                p.font.color.rgb = brand.ink
                p.space_after = Pt(0)
        table.rows[i].height = Inches(.63)
        pill = next(q for q in s(3).shapes if q.name == f'SCR pill {i}')
        replace(pill, row[1])
        pill.top = Inches(1.96 + .38 + (i-1)*.63 + .075)
    for q in s(3).shapes:
        if q.name == 'Unified source footer':
            replace(q, 'S = Situation   C = Complication   R = Resolution. Sources: SARS trade, departmental sales and published plant/site evidence. Detailed qualifications accompany the exhibits.')

    # Product-specific trade presentation. Preserve the native chart data.
    title(s(4), entries[4]['title'])
    right_panel(s(4), entries[4]['sections'][:3], brand, entries[4]['sections'][3])
    for q in s(4).shapes:
        if not q.has_text_frame:
            continue
        if q.text.startswith('Net imports:'):
            replace(q, 'Net imports: diesel 9.997 bn litres; petrol 3.081 bn litres.')
        elif q.text.startswith('Petrol + diesel |'):
            replace(q, 'Petrol and diesel, 2024, bn litres')
    s(4).notes_slide.notes_text_frame.text += '\n' + entries[4]['speaker_note']

    # Provincial shares and legends, with room above the original map.
    title(s(5), entries[5]['title'])
    clear(s(5), right=True)
    text(s(5), 'Provincial contribution', 8.12, 1.78, 4.03, .34, 17, True, brand.ink)
    shares=[list(row) for row in entries[5]['table']]
    shares[2][0]='KZN'
    native_table(s(5), shares, 8.12, 2.38, [1.63, 1.20, 1.20], [.45]+[.39]*4, brand, 11)
    text(s(5), 'Gauteng and KZN together account for 50.7% of reported sales.', 8.12, 4.68, 4.03, .65, 13, True, brand.ink)
    text(s(5), entries[5]['note'], 8.12, 5.59, 4.03, 1.0, 11.5, color=brand.ink)
    for q in list(s(5).shapes):
        y = q.top / Inches(1)
        if q.left >= Inches(7.6):
            continue
        if 2.37 <= y < 6.38:
            q.top = Inches(2.92 + (y-2.38)*.865)
            if not (q.has_text_frame and q.text.strip()):
                q.height = max(1, int(q.height*.865))
        elif 6.44 <= y <= 6.90:
            q.top = Inches(2.27 + (y-6.45))

    # Standardise the existing legends without changing chart values.
    for q in s(7).shapes:
        if q.left < Inches(7.6) and Inches(6.19) <= q.top <= Inches(6.26):
            q.top -= Inches(3.94)
        elif q.left < Inches(7.6) and Inches(2.40) <= q.top < Inches(6.0):
            q.top += Inches(.18)
    for q in s(17).shapes:
        if q.name == 'Footprint legend' or (q.has_text_frame and q.text in ('Vopak', 'Other listed') and q.left < Inches(7.6)):
            q.top -= Inches(.64)
    for q in s(20).shapes:
        if q.name in ('Demand legend', 'Handling legend') or (q.has_text_frame and q.text in ('Reported demand', 'Vopak', 'Other listed') and q.left < Inches(7.6)):
            q.top -= Inches(.54)
        elif q.has_text_frame and q.text.startswith('Base estimate:'):
            q.top = Inches(2.65)

    # Gateway competition is an observed footprint with a market-change question.
    title(s(16), entries[16]['title'])
    right_panel(s(16), entries[16]['sections'], brand,
                ('Current work', 'Compare the same product and inland destination. Record existing operations separately from proposed facilities.'))
    for q in s(16).shapes:
        if q.has_text_frame and q.text.startswith('Durban, Matola and Walvis Bay |'):
            replace(q, 'Existing gateways and potential inland distribution nodes')
        elif q.has_text_frame and q.text == 'Gauteng':
            replace(q, 'Gauteng demand');q.width = Inches(1.25)
    s(16).notes_slide.notes_text_frame.text += '\n' + entries[16]['note']

    # Explain the already-present road-cost surface at its point of use.
    title(s(15),'C5. The cost illustration compares road delivery from Durban and Lesedi')
    for q in s(15).shapes:
        if q.has_text_frame and q.text.startswith('Darker cells show'):
            replace(q,'Each 25 km cell shows the lower illustrative road cost from Durban or Lesedi. Destinations are grid cells, not customers.')

    # Practical site implications replace the playbook vocabulary.
    clear(s(22))
    title(s(22), entries[22]['title'])
    rows = [['Site', 'Current evidence', 'Implication for Vopak', 'Evidence still needed']] + entries[22]['rows']
    native_table(s(22), rows, .5, 2.12, [1.25, 3.5, 3.30, 3.60], [.46]+[1.10]*3, brand, 12)
    text(s(22), entries[22]['closing_copy'], .5, 6.26, 11.65, .55, 13, True, brand.ink)
    for q in s(22).shapes:
        if q.name == 'Unified source footer':
            replace(q, 'Source: 2022 departmental provincial sales; SARS 2024 trade; published Vopak, Matola and Walvis Bay inventory; Transnet lease offers. Additional Vopak volumes remain unquantified.')

    # Current work is explicit, without declaring the whole workstream complete.
    title(s(23), entries[23]['title'])
    table = next(q.table for q in s(23).shapes if q.has_table)
    labels = {1:'1  Fuel baseline - ACTIVE NOW', 2:'2  Assumption review - ACTIVE NOW', 7:'Storyline and evidence - ACTIVE NOW'}
    for row, label in labels.items():
        cell = table.cell(row, 0);cell.text = label
        for p in cell.text_frame.paragraphs:
            p.font.name=cfg.THEME_FONT;p.font.size=Pt(10);p.font.bold=True;p.font.color.rgb=brand.accent_primary
        cell=table.cell(row,3);cell.text='ACTIVE';cell.fill.solid();cell.fill.fore_color.rgb=brand.accent_primary
        for p in cell.text_frame.paragraphs:
            p.font.name=cfg.THEME_FONT;p.font.size=Pt(9);p.font.bold=True;p.font.color.rgb=brand.white
    for q in s(23).shapes:
        if not q.has_text_frame:continue
        if q.text.startswith('Proposed delivery sequence'):
            replace(q,'Current activity and proposed delivery sequence, as at 7 October 2026')
        elif q.text.startswith('Week 1 check:'):
            replace(q,'Active: source reconciliation, sector baselines and assumption definitions. Forecast runs follow reviewed inputs.')
        elif q.text.startswith('Weekly technical'):
            replace(q,'ACTIVE = current work; grey = proposed timing; diamonds = proposed checkpoints. Active does not mean complete.')
    s(23).notes_slide.notes_text_frame.text += '\n' + entries[23]['active_scope']

    # The illustrations stay available together, beyond the appendix divider.
    moved=[18,19,21]
    supporting_titles=next(p['supporting_titles'] for p in spec['pages'] if p.get('pages')==moved)
    for page,value in zip(moved,supporting_titles):
        title(s(page),value)
        for q in list(s(page).shapes):
            if q.name.startswith('Section navigation '):remove(q)
        s(page).notes_slide.notes_text_frame.text += '\nSupporting illustration only. Not an estimate of additional Vopak volumes or investment needs.'
    for q in s(18).shapes:
        if q.has_text_frame and q.text.startswith('Receipts of 2.8 plus'):
            replace(q,'The 3.0 result removes the shared transfer and assumes no net stock change or other adjustments. Actual flows remain unverified.')
    order=[n for n in range(1,26) if n not in moved]+moved+list(range(26,32))
    mapping={old:new for new,old in enumerate(order,1)}
    ids=list(prs.slides._sldIdLst)
    for item in ids:prs.slides._sldIdLst.remove(item)
    for n in order:prs.slides._sldIdLst.append(ids[n-1])
    page_by_part={slide.part:i for i,slide in enumerate(prs.slides,1)}
    for slide in prs.slides:
        frames=[q.text_frame for q in slide.shapes if q.has_text_frame]
        frames += [c.text_frame for q in slide.shapes if q.has_table for row in q.table.rows for c in row.cells]
        for frame in frames:
            if '20.763 bn L' in frame.text:
                frame.text='Reported 2024 sales: petrol 9.029 bn L and diesel 11.734 bn L. Coverage awaits reconciliation. Provincial history ends in 2022.'
                for p in frame.paragraphs:p.font.name=cfg.THEME_FONT;p.font.size=Pt(10);p.font.color.rgb=brand.ink
            for p in frame.paragraphs:
                for run in p.runs:
                    run.text=run.text.replace('S/C3','C3')
                    for h in run._r.xpath('.//a:hlinkClick'):
                        rid=h.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                        if rid and not slide.part.rels[rid].is_external:
                            target=slide.part.rels[rid].target_part
                            if target in page_by_part and re.fullmatch(r'\s*(?:/\s*)?\d+\s*',run.text):
                                run.text=(' / ' if '/' in run.text else '')+str(page_by_part[target])
        for q in slide.shapes:
            if not q.has_text_frame:continue
            value=q.text
            if '20.763 bn L' in value:value=value.replace('20.763 bn L','petrol 9.029 bn L and diesel 11.734 bn L')
            if 'Operator footprint on p17; handling on p20' in value:value=value.replace('handling on p20','handling on p18')
            if 'page 19' in value:value=value.replace('page 19','page 24')
            if 'Every Henry storyboard prompt' in value:value=re.sub(r'pages \d+[–-]\d+', 'the supporting response pages',value)
            if q.name=='Unified source footer' and 'Authored market hypotheses' in value:value=value.replace('pp.4, 11–19','the demand, gateway and footprint exhibits')
            if value!=q.text:replace(q,value)
    overview_table=next(q.table for q in s(3).shapes if q.has_table)
    links=[[4,7],[5,6],[8,9,11,12,13,14],[10,11,12,13,14],[15,16],[17,20],[22,23,24]]
    for r,pages in enumerate(links,1):_links(s(3),overview_table.cell(r,4),[mapping[p] for p in pages],prs,brand)
    # Preserve the master, but use explicit numbers after the reordered slides.
    for n,slide in enumerate(prs.slides,1):
        for q in slide.shapes:
            if q.has_text_frame and q.name=='Slide Number Placeholder':
                q.text=str(n)
                for p in q.text_frame.paragraphs:p.font.name=cfg.THEME_FONT;p.font.size=Pt(10);p.font.color.rgb=brand.ink
        for q in slide.shapes:
            assert q.left>=0 and q.top>=0 and q.left+q.width<=prs.slide_width+10 and q.top+q.height<=prs.slide_height+10,(n,q.name)
    return mapping


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    source=Path(sys.argv[1]);output=Path(sys.argv[2])
    if output.exists():output=next_version_path(output)
    prs=Presentation(source)
    mapping=apply_annotated_review(prs,root,BrandStyle.from_module(cfg))
    prs.save(output)
    output.with_suffix('.review.json').write_text(json.dumps({'source':str(source),'output':str(output),'original_to_revised_page':mapping},indent=2),encoding='utf-8')
    print(output)
