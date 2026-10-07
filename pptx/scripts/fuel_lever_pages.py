"""Three template-based review pages displaying registered draft input snapshots."""
import csv,json,re
from pptx.util import Inches,Pt
from pptx.enum.text import MSO_ANCHOR
from brand_pptx import add_themed_slide,_strip_table_style,cell_bottom_rule
from convergence_feedback import text,replace,line
from driver_split import clone_shape
from brand_configs import vopak as cfg


def add_fuel_lever_pages(prs,root,brand):
    assert len(prs.slides)==27
    doc=json.loads((root/'story/fuel_lever_design_2026_10_07.json').read_text(encoding='utf-8'))
    rows=list(csv.DictReader((root.parent/'assumptions/2026/timeseries/fuel_lever_design_2026_10_07.csv').open(encoding='utf-8-sig')))
    inputs={(r['fuel'],r['lever'],int(r['period']),r['case']):r['value'] for r in rows}
    original=list(prs.slides);oldpages={s.part:i for i,s in enumerate(original,1)}
    framework=original[10]
    for q in framework.shapes:
        if q.has_text_frame and q.text=='Agreed reference assumptions':replace(q,'Proposed M settings; fuel inputs follow')
    framework.notes_slide.notes_text_frame.text+='\n7 October: explicit diesel, jet and petrol draft L/M/H inputs now follow at 2030 and 2035. These are review proposals, not calibrated or engine-consumed scenarios. Customer-access and operational settings remain separate tasks.'
    from convergence_story_order import clone_navigation
    new=[]
    for fuel in doc['fuels']:
        s=add_themed_slide(prs,'Header only',brand=brand,title=fuel['title']);new.append(s)
        clone_navigation(s,framework)
        for q in framework.shapes:
            if q.name=='Strictly Confidential footer':clone_shape(q,framework,s)
        title=next(q for q in s.shapes if q.name=='Title 1')
        for p in title.text_frame.paragraphs:
            p.font.size=Pt(24);p.font.bold=True
            for r in p.runs:r.font.size=Pt(24);r.font.bold=True
        text(s,f'{fuel["fuel"].capitalize()} levers | proposed input values for review',.5,1.78,11.65,.32,14,True)
        line(s,(.5,2.13),(12.15,2.13),brand.ink,.55)
        text(s,'L / M / H means low / medium / high input level; fuel effects differ by lever. M is a proposed reference.',.5,2.25,11.65,.27,11)
        content=[['Lever / unit','Current reference','2030\nL / M / H','2035\nL / M / H','Rationale / effect']]
        for lever in fuel['levers']:
            vals=[]
            for year in doc['horizons']:
                vals.append(' / '.join(f'{float(inputs[fuel["fuel"],lever["id"],year,case]):g}' for case in doc['case_order']))
            content.append([lever['label'],lever['reference'],*vals,lever['rationale']])
        sh=s.shapes.add_table(len(content),5,Inches(.5),Inches(2.72),Inches(11.65),Inches(3.76));t=sh.table;_strip_table_style(t)
        for col,w in zip(t.columns,[2.27,2.05,1.53,1.53,4.27]):col.width=Inches(w)
        for i,row in enumerate(content):
            t.rows[i].height=Inches(.43 if i==0 else (3.76-.43)/(len(content)-1))
            for j,value in enumerate(row):
                c=t.cell(i,j);c.text=value;c.fill.solid();c.fill.fore_color.rgb=brand.white
                c.margin_left=c.margin_right=Inches(.035);c.margin_top=Inches(.035);c.margin_bottom=0;c.vertical_anchor=MSO_ANCHOR.TOP
                for p in c.text_frame.paragraphs:
                    p.font.name=cfg.THEME_FONT;p.font.size=Pt(10.5 if j==4 else 11);p.font.bold=i==0;p.font.color.rgb=brand.ink;p.space_after=Pt(0)
                cell_bottom_rule(c,color=brand.grey_fill,w_pt=.5)
        text(s,fuel['bridge'],.5,6.61,11.65,.34,11)
        text(s,'Source: Registered draft fuel_lever_design inputs, 7 Oct 2026; existing input anchors and primary-source URLs in notes. Review outstanding.',.5,7.10,10.2,.26,7.5).name='Unified source footer'
        s.notes_slide.notes_text_frame.text=json.dumps({'status':doc['status'],'fuel':fuel,'sources':doc['sources'],'handoff':'Not yet consumed by engine. Percentages are stored as display percentages: divide by 100 when mapping to model fractions. Define annual paths from a matched opening year through 2030 and 2035; do not interpolate silently. Shared utilisation and restart must be identical across all fuel pages. Yield slates must sum to <=100% including other products. ACSA excludes non-ACSA airports; movement model must be re-estimated. SAF does not reduce total jet litres. Owners: Manish baseline/source and integration; Nigel range selection; Henry technical challenge.'},ensure_ascii=False,indent=2)
    ids=prs.slides._sldIdLst
    for offset,s in enumerate(new):
        ident=next(q for q in ids if prs.part.related_slide(q.rId).part==s.part);ids.remove(ident);ids.insert(11+offset,ident)
    pages={s.part:i for i,s in enumerate(prs.slides,1)}
    for s in prs.slides:
        frames=[q.text_frame for q in s.shapes if q.has_text_frame]+[c.text_frame for q in s.shapes if q.has_table for row in q.table.rows for c in row.cells]
        for tf in frames:
            for p in tf.paragraphs:
                for r in p.runs:
                    for h in r._r.xpath('.//a:hlinkClick'):
                        rid=h.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                        if rid and not s.part.rels[rid].is_external and s.part.rels[rid].target_part in pages:r.text=re.sub(r'\d+',str(pages[s.part.rels[rid].target_part]),r.text)
        for q in s.shapes:
            if not q.has_text_frame:continue
            v=q.text.replace('pages 23–25','pages 26–28').replace('on page 16','on page 19').replace('footprint on p14; handling on p17','footprint on p17; handling on p20').replace('pp.4, 11–16','pp.4, 11–19')
            if v!=q.text:replace(q,v)
            if q.top>Inches(7) and q.left>Inches(12) and q.text.strip().isdigit():replace(q,str(pages[s.part]))
    # Every main-story analytical page is covered by the summary.
    from agenda_answer_page import _links
    overview=original[2];t=next(q.table for q in overview.shapes if q.has_table)
    for row,targets in enumerate([[4,7],[5,6],[8,9,11,12,13,14],[10,11,12,13,14],[15,16],[17,18,19,20],[21,22,23]],1):_links(overview,t.cell(row,4),targets,prs,brand)
    # Power, price and electrification evidence moved to the second driver page.
    trace_links={
        'Greater diesel use in power generation':[9,12],
        'Rail to road':[8,12],
        'Changes in fuel price':[9,11],
        'More fuel-efficient vehicles':[9,12,14],
        'Slow GDP growth':[8,14],
        'Road to rail; private-sector rail projection':[8,12],
        'End of loadshedding and spare power capacity':[9,12],
        'EV / HEV penetration projection':[9,14],
        'Effect of EV / HEV on litres per km':[9,14],
        'Higher fuel prices and km travelled':[9,14],
        'Mega refinery / SAPREF restart':[10,12,13,14]
    }
    for s in prs.slides:
        for q in s.shapes:
            if not q.has_table:continue
            for row in q.table.rows:
                if row.cells[0].text in trace_links:_links(s,row.cells[len(row.cells)-1],trace_links[row.cells[0].text],prs,brand)
    # Aviation lever design is newly requested; the measured market evidence remains petrol/diesel.
    scope=original[1]
    for q in scope.shapes:
        if q.has_text_frame and q.text.startswith('Demand drivers, refinery alternatives'):
            replace(q,'Diesel, jet and petrol lever design at 2030 and 2035; draft L/M/H inputs for demand and domestic output.')
    from footer_layout import finish_footer_and_markers
    finish_footer_and_markers(prs,brand)
    for s in prs.slides:
        nodes=s._element.xpath('.//p:cNvPr');seen=set();nextid=max(int(q.get('id')) for q in nodes)+1
        for q in nodes:
            if q.get('id') in seen:q.set('id',str(nextid));nextid+=1
            seen.add(q.get('id'))
    assert len(prs.slides)==30
