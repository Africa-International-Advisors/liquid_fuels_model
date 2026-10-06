"""Two readable four-chart driver pages, preserving native data and slide links."""
from copy import deepcopy
import re
from pptx.util import Inches,Pt
from brand_pptx import add_themed_slide
from convergence_feedback import text,replace


def clone_shape(q,source,dest):
    el=deepcopy(q._element)
    ns='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
    for node in el.iter():
        for a,rid in list(node.attrib.items()):
            if a.startswith(ns):
                rel=source.part.rels[rid]
                node.set(a,dest.part.relate_to(rel.target_ref if rel.is_external else rel.target_part,rel.reltype,is_external=rel.is_external))
    dest.shapes._spTree.insert_element_before(el,'p:extLst')
    return dest.shapes[-1]


def split_drivers(prs,root,brand):
    assert len(prs.slides)==26
    source=prs.slides[7]
    dest=add_themed_slide(prs,'Header only',brand=brand,title='S/C3. Test diesel power, vehicle mix and prices alongside industrial demand')
    # The supplied corporate layout remains the master for both pages.
    from convergence_story_order import clone_navigation
    clone_navigation(dest,source)
    for q in source.shapes:
        if q.name=='Strictly Confidential footer' or q.name=='Unified source footer':clone_shape(q,source,dest)
    groups=[]
    for row in range(4):
        for col in range(2):
            x=.5+6*col;y=2.51+1.08*row
            groups.append([q for q in source.shapes if abs(q.left/Inches(1)-x)<5.66 and x<=q.left/Inches(1)<x+5.66 and y-.01<=q.top/Inches(1)<y+1.02])
    for idx,group in enumerate(groups):
        target=source if idx<4 else dest
        slot=idx%4;row=slot//2;col=slot%2
        old_y=2.51+(idx//2)*1.08;new_y=2.45+2.29*row
        for original in group:
            q=original if target==source else clone_shape(original,source,dest)
            if q.has_chart:
                q.top=Inches(new_y+.37);q.height=Inches(1.30)
                # Let PowerPoint reserve room for the larger native axis labels.
                for layout in q.chart._chartSpace.xpath('.//c:plotArea/c:layout'):
                    layout.getparent().remove(layout)
                for axis in (q.chart.value_axis,q.chart.category_axis):
                    axis.has_major_gridlines=False;axis.has_minor_gridlines=False
                    axis.tick_labels.font.size=Pt(10)
            elif abs(original.top/Inches(1)-old_y)<.05:
                q.top=Inches(new_y);q.height=Inches(.30)
            else:
                q.top=Inches(new_y+1.91+(original.top/Inches(1)-(old_y+.87)))
                if q.has_text_frame:
                    q.height=Inches(.24)
                    for p in q.text_frame.paragraphs:
                        p.font.size=Pt(11)
                        for r in p.runs:r.font.size=Pt(11)
        if target==dest:
            for q in group:q._element.getparent().remove(q._element)
    # Refresh subtitles and remove the cramped old dashboard note.
    for q in source.shapes:
        if q.name=='Title 1':replace(q,'S/C3. Test passenger, freight and sector activity separately before forecasting fuel demand')
        elif q.has_text_frame and abs(q.top-Inches(1.78))<10:replace(q,'Activity drivers | observed series; 2024 = 100')
        elif q.has_text_frame and q.text.startswith('Observed proxies,'):
            replace(q,'Observed activity proxies; fuel use per unit still requires validation.')
    text(dest,'Power, vehicle mix and prices | observed indices and nominal R/litre',.5,1.78,11.65,.32,14,True)
    text(dest,'Indices: 2024 = 100. Prices: nominal R/litre. OCGT generation: FY to March.',.5,2.20,11.65,.22,10)
    from supply_review_pages import line
    line(dest,(.5,2.13),(12.15,2.13),brand.ink,.55)
    for s in (source,dest):
        title=next(q for q in s.shapes if q.name=='Title 1')
        for p in title.text_frame.paragraphs:
            p.font.size=Pt(24);p.font.bold=True
            for r in p.runs:r.font.size=Pt(24);r.font.bold=True
    dest.notes_slide.notes_text_frame.text=source.notes_slide.notes_text_frame.text+'\nFour-chart second driver page; native series and periods preserved. Mining, diesel power, vehicle sales and fuel prices remain separate proxies, not a fuel forecast.'
    ids=prs.slides._sldIdLst;new=ids[-1];ids.remove(new);ids.insert(8,new)
    pages={s.part:i for i,s in enumerate(prs.slides,1)}
    # Internal links follow slide identities rather than the old visible numbers.
    for s in prs.slides:
        frames=[q.text_frame for q in s.shapes if q.has_text_frame]
        frames += [c.text_frame for q in s.shapes if q.has_table for row in q.table.rows for c in row.cells]
        for tf in frames:
            for p in tf.paragraphs:
                for r in p.runs:
                    for h in r._r.xpath('.//a:hlinkClick'):
                        rid=h.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                        if rid and not s.part.rels[rid].is_external and s.part.rels[rid].target_part in pages:
                            r.text=re.sub(r'\d+',str(pages[s.part.rels[rid].target_part]),r.text)
        for q in s.shapes:
            if not q.has_text_frame:continue
            # Only known authored internal references; leave source publication page numbers intact.
            v=q.text
            v=v.replace('pages 22–24','pages 23–25').replace('on page 15','on page 16')
            v=v.replace('footprint on p13; handling on p16','footprint on p14; handling on p17')
            v=v.replace('pp.4, 10–15','pp.4, 11–16')
            if v!=q.text:replace(q,v)
            if q.top>Inches(7) and q.left>Inches(12) and q.text.strip().isdigit():replace(q,str(pages[s.part]))
    from agenda_answer_page import _links
    overview=prs.slides[2];table=next(q.table for q in overview.shapes if q.has_table)
    for row,targets in enumerate([[4,7],[5,6],[8,9,11],[10,11],[12,13],[14,15,16,17],[18,19,20]],1):
        _links(overview,table.cell(row,4),targets,prs,brand)
    from footer_layout import finish_footer_and_markers
    finish_footer_and_markers(prs,brand)
    # Remapped clones require unique slide-local shape identifiers.
    for s in prs.slides:
        nodes=s._element.xpath('.//p:cNvPr');seen=set();n=max(int(q.get('id')) for q in nodes)+1
        for q in nodes:
            if q.get('id') in seen:q.set('id',str(n));n+=1
            seen.add(q.get('id'))
    assert len(prs.slides)==27
