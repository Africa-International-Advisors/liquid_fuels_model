"""Answer-led sequence and kickoff-plan delivery checks; no forecast execution."""
import csv
import json
import re
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from brand_pptx import add_themed_slide, _strip_table_style, cell_bottom_rule
from brand_configs import vopak as cfg
from convergence_feedback import text, bar, line, clear_body, replace, inventory
from terminal_turnover_page import turnover_cases
from lfm.model.supply.terminal_handling import annual_handling_m3


def regional_footprint(s, root, brand):
    clear_body(s, True)
    for q in s.shapes:
        if not q.has_text_frame: continue
        if q.name == 'Title 1': replace(q, 'R6. Group the storage footprint into eastern, inland and western markets')
        elif abs(q.top-Inches(1.78))<10 and q.left<Inches(8):replace(q,'Regional footprint | published gross storage, thousand m³')
        elif q.text.startswith('01 |'):replace(q,'01 | Regions organise the market test')
        elif q.text.startswith(('At 1 / 2 / 3','Published tank volumes')):replace(q,'Use these regions to align demand, reach and annual handling. Site catchments require customer and route evidence.')
    text(s,'Region / provinces',.5,2.40,1.8,.25,10,True)
    text(s,'Storage location',2.2,2.40,1.8,.25,10,True)
    text(s,'Published tank capacity',4.0,2.40,3.4,.25,10,True)
    for x,label,col in [(4.0,'Vopak',brand.accent_primary),(5.3,'Other listed',brand.accent_secondary)]:
        bar(s,x,2.89,.12,.12,col,'Footprint legend');text(s,label,x+.18,2.84,1.5,.24,9)
    x0=4.0;w=2.65;maximum=850
    for tick in [0,200,400,600,800]:
        x=x0+w*tick/maximum;text(s,str(tick),x-.10,3.16,.42,.23,9)
        line(s,(x,3.48),(x,6.10),brand.grey_fill,.5)
    groups=[('Eastern coast','EC/KZN',['Durban','Richards Bay']),('Inland','GP/FS/LP/MP/NW',['Lesedi','Isando']),('Western coast','WC',['Cape Town']),('Other','NC',[])]
    data=inventory(root);y=3.60
    for region,provinces,sites in groups:
        text(s,region,.5,y,1.6,.25,11);text(s,provinces,.5,y+.27,1.6,.23,8.5)
        for site in sites:
            text(s,site,2.2,y,1.65,.25,11);xx=x0;total=0
            for is_vopak in (True,False):
                rows=[r for r in data if r['site']==site and bool(r.get('gross_capacity_m3')) and (r['operator']=='Vopak')==is_vopak]
                cap=sum(float(r['gross_capacity_m3']) for r in rows)/1000
                if cap:
                    ww=w*cap/maximum;bar(s,xx,y+.01,ww,.23,brand.accent_primary if is_vopak else brand.accent_secondary,'Published gross '+site);xx+=ww;total+=cap
            text(s,f'{total:.2f}',xx+.07,y-.01,.75,.26,10)
            y+=.40
        if not sites:
            text(s,'?  capacity not established',2.2,y,4.8,.26,11);y+=.40
        y+=.18
    text(s,'Partial inventory; mixed products. Unlisted capacities remain unknown.',.5,6.53,7.05,.26,10)
    text(s,'Mixed products; lease offers excluded. Working fuel space and customer share remain unverified.',.5,6.77,7.05,.21,8.5)
    s.notes_slide.notes_text_frame.text+='\nRegional reporting groups match the demand-map membership CSV. Primary gross inventory is unchanged; conditional lease volumes remain in source CSV and notes, not operating bars. Northern Cape coverage incomplete.'


def native_table(s, rows, x, y, widths, heights, brand, size=10):
    q=s.shapes.add_table(len(rows),len(widths),Inches(x),Inches(y),Inches(sum(widths)),Inches(sum(heights)))
    t=q.table;_strip_table_style(t)
    for col,w in zip(t.columns,widths):col.width=Inches(w)
    for i,row in enumerate(rows):
        t.rows[i].height=Inches(heights[i])
        for j,v in enumerate(row):
            c=t.cell(i,j);c.text=str(v);c.margin_left=Inches(.04);c.margin_right=Inches(.03);c.margin_top=Inches(.05);c.margin_bottom=0
            c.fill.solid();c.fill.fore_color.rgb=brand.white
            for p in c.text_frame.paragraphs:
                p.font.name=cfg.THEME_FONT;p.font.size=Pt(size);p.font.bold=i==0;p.font.color.rgb=brand.ink;p.space_after=Pt(0)
            cell_bottom_rule(c,color=brand.grey_fill,w_pt=.5)
    return t


def delivery_roadmap(prs, root, brand):
    d=json.loads((root/'story/convergence_delivery_plan_2026_10_06.json').read_text(encoding='utf-8'))
    s=add_themed_slide(prs,'Header only',brand=brand,title='R7. Use the six-week workplan to test the evidence and align client decisions')
    text(s,'Proposed delivery sequence | evidence gates and client touchpoints',.5,1.78,11.65,.34,14,True)
    rows=[['Activity / workstream','Resources']+d['weeks']]
    rows += [[r['activity'],r['owner']]+['']*6 for r in d['rows']]
    t=native_table(s,rows,.5,2.37,[4.10,1.85]+[.95]*6,[.55]+[.37]*7,brand,10)
    for i,r in enumerate(d['rows'],1):
        for week in r['active']:
            c=t.cell(i,week+1);c.fill.fore_color.rgb=brand.accent_secondary if i==7 else brand.grey_fill
            # A navy square marks the proposed evidence gate, not completion.
            if week==r['gate_week']:
                c.text='◆';c.text_frame.paragraphs[0].font.color.rgb=brand.accent_primary
                c.text_frame.paragraphs[0].font.size=Pt(14)
    text(s,'Client touchpoints',.5,5.70,2.9,.26,11,True)
    for touch in d['client_touchpoints']:
        x=.5+4.10+1.85+(touch['week']-1)*.95+.39
        q=s.shapes.add_shape(MSO_SHAPE.DIAMOND,Inches(x),Inches(5.75),Inches(.12),Inches(.12));q.fill.solid();q.fill.fore_color.rgb=brand.accent_primary;q.line.fill.background()
        text(s,touch['label'].replace('Scope / data','Scope /\ndata').replace('Emerging findings','Emerging\nfindings').replace('Draft implications','Draft\nimplications').replace('Final review','Final\nreview'),x-.31,5.99,.94,.43,8.5)
    text(s,'Week 1 check: baseline reproduced and evidence assembled; reconciliation and acceptance remain open.',.5,6.43,11.65,.28,10.5,True)
    text(s,'Weekly technical / partner reviews; client W1 / W3 / W5 / W6. ◆ = proposed gate or touchpoint. Handover target: 12 Nov; dates to agree.',.5,6.78,11.65,.26,9)
    text(s,'Source: Kickoff pack pp23–27; six_week_plan.md (fuel-first update). Proposed workplan; no review or client approval inferred.',.5,7.10,10.2,.23,7.5)
    s.notes_slide.notes_text_frame.text=json.dumps(d,ensure_ascii=False,indent=2)
    return s


def turnover_appendix(prs, root, brand):
    rates=turnover_cases(root);data=inventory(root)
    s=add_themed_slide(prs,'Header only',brand=brand,title='Supporting sensitivity | monthly turns change estimated annual handling')
    text(s,'Gross handling equivalent, million m³/year | authored 1 / 2 / 3 monthly-turn cases',.5,1.78,11.65,.4,14,True)
    rows=[['Region','Low: 1 turn/month','Base: 2 turns/month','High: 3 turns/month']]
    for name,sites in [('Eastern coast',['Durban','Richards Bay']),('Inland',['Lesedi','Isando']),('Western coast',['Cape Town']),('Other / NC',[])]:
        selected=[r for r in data if r['site'] in sites and r.get('gross_capacity_m3')]
        cap=sum(float(r['gross_capacity_m3']) for r in selected)
        rows.append([name]+[f'{annual_handling_m3(cap,rates[k])/1e6:.2f}' if selected else 'Unknown' for k in ('low','base','high')])
    native_table(s,rows,.5,2.65,[3.05,2.85,2.85,2.9],[.50]+[.50]*4,brand,13)
    text(s,'Annual handling = gross tankage × monthly turns × 12',.5,5.52,11.65,.35,15,True)
    text(s,'Two turns/month is an authored base. The range is informed by generic industry material, not measured SA site performance. Replace with compatible working capacity and unique outbound volumes.',.5,6.06,11.65,.55,12)
    text(s,'Partial inventory and mixed products; no available-supply, regional-shortage or market-share conclusion. Coastal/inland handling can count the same transferred fuel twice.',.5,6.78,11.65,.28,9)
    text(s,'Source: Registered terminal_handling.yaml; site inventory; Blackmer/Dover 2013 and Wood Mackenzie 2009. Owner: Manish / Nigel.',.5,7.10,10.2,.23,7.5)
    s.notes_slide.notes_text_frame.text=(root/'story/terminal_turnover_evidence_2026_10_06.json').read_text(encoding='utf-8')
    return s


def clone_navigation(dest, source):
    from copy import deepcopy
    ns='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
    for q in source.shapes:
        if not q.name.startswith('Section navigation '):continue
        el=deepcopy(q._element)
        for node in el.iter():
            for attr,rid in list(node.attrib.items()):
                if attr.startswith(ns):
                    rel=source.part.rels[rid]
                    node.set(attr,dest.part.relate_to(rel.target_ref if rel.is_external else rel.target_part,rel.reltype,is_external=rel.is_external))
        dest.shapes._spTree.insert_element_before(el,'p:extLst')


def apply_story_order(prs, root, brand):
    """Input is the 24-page convergence feedback output; preserve slide identities."""
    assert len(prs.slides)==24
    old=list(prs.slides)
    regional_footprint(old[14],root,brand)
    # Working stock follows the opportunity and annual handling tests in the main story.
    from storage_sensitivity_page import add_storage_sensitivity_page
    add_storage_sensitivity_page(old[18],text,root,brand)
    for q in old[18].shapes:
        if q.name=='Title 1':replace(q,'R7. Illustrative additional flows need 211,000 m³ at 14 inventory days')
        elif q.has_text_frame and q.text.startswith('Illustrative: 5.5'):replace(q,'Illustrative 5.5 bn litres/year from the opportunity waterfall')
    clone_navigation(old[18],old[15])
    chart=next(q.chart for q in old[18].shapes if q.has_chart)
    for point in chart.series[0].points:
        point.format.fill.solid();point.format.fill.fore_color.rgb=brand.grey_fill
    chart.series[0].points[1].format.fill.fore_color.rgb=brand.accent_primary
    chart.plots[0].data_labels.font.bold=False
    roadmap=delivery_roadmap(prs,root,brand);sensitivity=turnover_appendix(prs,root,brand)
    clone_navigation(roadmap,old[15])
    # Cover / scope / answer / market evidence / footprint / opportunity / handling / stock / decision / delivery.
    order=[old[0],old[17],old[1]]+old[2:11]+[old[14],old[11],old[13],old[12],old[18],old[15],roadmap,old[16],sensitivity]+old[19:]
    sid_by_part={prs.part.related_slide(r.rId).part:r for r in prs.slides._sldIdLst}
    for r in list(prs.slides._sldIdLst):prs.slides._sldIdLst.remove(r)
    for s in order:prs.slides._sldIdLst.append(sid_by_part[s.part])
    pages={s.part:i for i,s in enumerate(prs.slides,1)}
    # Refresh visible hyperlink labels from their actual target identities, including Henry trace tables.
    for s in prs.slides:
        frames=[q.text_frame for q in s.shapes if q.has_text_frame]
        frames += [c.text_frame for q in s.shapes if q.has_table for row in q.table.rows for c in row.cells]
        for f in frames:
            for p in f.paragraphs:
                for r in p.runs:
                    for h in r._r.xpath('.//a:hlinkClick'):
                        rid=h.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                        if rid and not s.part.rels[rid].is_external and s.part.rels[rid].target_part in pages:r.text=re.sub(r'\d+',str(pages[s.part.rels[rid].target_part]),r.text)
        for q in s.shapes:
            if not q.has_text_frame:continue
            if 'Every Henry storyboard prompt' in q.text:replace(q,re.sub(r'pages \d+[–-]\d+','pages 22–24',q.text))
            elif q.text.startswith('The main story ends'):replace(q,'The main story ends with the outlook and delivery roadmap.')
            elif q.text.startswith('Document scope ·'):replace(q,'Turnover sensitivity · Henry storyboard responses · presentation palette')
            if q.top>Inches(7) and q.left>Inches(12) and q.text.strip().isdigit():replace(q,str(pages[s.part]))
    # One overview row owns every analytical page; roadmap belongs to the decision row.
    from agenda_answer_page import _links
    overview=old[1];t=next(q.table for q in overview.shapes if q.has_table)
    groups=[[4,7],[5,6],[8,10],[9,10],[11,12],[13,14,15,16],[17,18,19]]
    for row,targets in enumerate(groups,1):_links(overview,t.cell(row,4),targets,prs,brand)
    for row,evidence,verdict in [
        (6,'Footprint → reach → estimated handling\nDefine regions, screen customers and compare annual demand with handling at two turns/month.','Footprint established; customer share unquantified.\nValidate cost, service, rights and unique deliveries.'),
        (7,'Working stock → outlook → delivery gates\nThe 5.5 bn L/year example needs 211,000 m³ at 14 days; test usable spare space before adding tanks.','Conditional: secure customer flows first.\nUse existing assets; validate a capacity gap, then test investment.')]:
        for col,value in [(2,evidence),(3,verdict)]:
            c=t.cell(row,col);c.text=value
            for p in c.text_frame.paragraphs:p.font.name=cfg.THEME_FONT;p.font.size=Pt(10.5);p.font.color.rgb=brand.ink;p.space_after=Pt(0)
    # Add a clear reference from the outlook to the stock and workplan tests.
    old[15].notes_slide.notes_text_frame.text+='\nMain-story decisions supported by p17 working inventory and p19 kickoff-aligned delivery gates; detailed turnover sensitivity in appendix p21. Client touchpoints W1/W3/W5/W6 remain proposed.'
    from scr_editorial import apply_confidentiality
    from footer_layout import finish_footer_and_markers
    apply_confidentiality(prs);finish_footer_and_markers(prs,brand)
    # Cloned editable map/navigation shapes must have unique slide-local IDs.
    for slide in prs.slides:
        nodes=slide._element.xpath('.//p:cNvPr');seen=set()
        next_id=max(int(n.get('id')) for n in nodes)+1
        for node in nodes:
            if node.get('id') in seen:
                node.set('id',str(next_id));next_id+=1
            seen.add(node.get('id'))
    assert len(prs.slides)==26
    from partner_review import apply_partner_review
    apply_partner_review(prs,root,brand)


if __name__=='__main__':
    import sys
    from pptx import Presentation
    from brand_pptx import BrandStyle
    root=Path(__file__).resolve().parents[1]
    p=Presentation(sys.argv[1]);b=BrandStyle.from_module(cfg)
    # Refresh changed exhibits before reordering their identities.
    from convergence_feedback import regional_graph, penetration_flow
    regional_graph(p.slides[12],root,b);penetration_flow(p.slides[13],root,b,p.slides[9])
    apply_story_order(p,root,b)
    for i,s in enumerate(p.slides,1):
        for q in s.shapes:assert q.left>=0 and q.top>=0 and q.left+q.width<=p.slide_width+10 and q.top+q.height<=p.slide_height+10,(i,q.name)
    p.save(sys.argv[2]);print('Built 26-page answer-led convergence pack')
