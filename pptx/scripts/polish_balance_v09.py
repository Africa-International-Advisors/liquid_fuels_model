from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from copy import deepcopy
from lxml import etree as E
import json
from lock_vopak_layout import NS,box,serial
r=Path(__file__).resolve().parents[2];q=r/'pptx/qa/evidence_v09'
with ZipFile(q/'with_chart_workbooks.pptx') as z:parts={n:z.read(n) for n in z.namelist()}
t=E.fromstring(parts['ppt/slides/slide2.xml']);sp=t.find('p:cSld/p:spTree',NS)
by={s.find('.//p:cNvPr',NS).get('name'):s for s in sp if s.find('.//p:cNvPr',NS) is not None}
with ZipFile(r/'pptx/templates/Vopak_Approved_Exhibit_Reference_v1.pptx') as z:ref=E.fromstring(z.read('ppt/slides/slide7.xml'))
refs={s.find('.//p:cNvPr',NS).get('name'):s for s in ref.find('p:cSld/p:spTree',NS) if s.find('.//p:cNvPr',NS) is not None}
for name,old in [('Vopak exhibit left heading','TextBox 2800'),('Vopak exhibit right heading','TextBox 3410')]:
 xf=by[name].find('p:spPr/a:xfrm',NS);xf.getparent().replace(xf,deepcopy(refs[old].find('p:spPr/a:xfrm',NS)))
for i,(txt,x,y,w,color) in enumerate([('Production',194,477,116,'FFFFFF'),('Imports',203,348,98,'FFFFFF'),('Consumption',490,390,134,'FFFFFF'),('Exports',632,282,90,'555555')]):
 s=deepcopy(refs['TextBox 2800']);pr=s.find('.//p:cNvPr',NS);pr.set('id',str(9900+i));pr.set('name','Balance stack label '+str(i));box(s,[x,y,w,23])
 body=s.find('p:txBody',NS)
 for p in list(body.findall('a:p',NS)):body.remove(p)
 p=E.SubElement(body,'{'+NS['a']+'}p');pp=E.SubElement(p,'{'+NS['a']+'}pPr',algn='ctr')
 run=E.SubElement(p,'{'+NS['a']+'}r');rp=E.SubElement(run,'{'+NS['a']+'}rPr',sz='1125');fill=E.SubElement(rp,'{'+NS['a']+'}solidFill');E.SubElement(fill,'{'+NS['a']+'}srgbClr',val=color);E.SubElement(rp,'{'+NS['a']+'}latin',typeface='Lato');E.SubElement(run,'{'+NS['a']+'}t').text=txt;sp.append(s)
parts['ppt/slides/slide2.xml']=serial(t)
with ZipFile(q/'reviewed_candidate.pptx','w',ZIP_DEFLATED) as z:
 for n,v in parts.items():z.writestr(n,v)
p=r/'pptx/brand_configs/vopak_layout.json';c=json.loads(p.read_text());c['deck_profiles']['evidence_v09']={'navigation_pages':list(range(2,16)),'exhibit_pages':[2,4,5,6,7,8,9,10,11,14]};p.write_text(json.dumps(c,indent=2)+'\n')
