from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
from copy import deepcopy
r=Path(__file__).resolve().parents[2];q=r/'pptx/qa/evidence_v06'
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
with ZipFile(q/'with_chart_workbooks.pptx') as z:parts={n:z.read(n) for n in z.namelist()}
base=E.fromstring(parts['ppt/slides/slide4.xml'])
sample=next(s for s in base.findall('.//p:sp',ns) if s.find('p:nvSpPr/p:cNvPr',ns).get('name')=='Evidence divider')
for page,boxes in [(9,[(48,210,745,1),(835,210,332,1),(816,173,1,390)]),(10,[(48,210,500,1),(590,210,576,1),(570,173,1,440)])]:
 name=f'ppt/slides/slide{page}.xml';t=E.fromstring(parts[name]);sp=t.find('p:cSld/p:spTree',ns)
 for i,(x,y,w,h) in enumerate(boxes):
  sh=deepcopy(sample);pr=sh.find('p:nvSpPr/p:cNvPr',ns);pr.set('id',str(9000+i));pr.set('name',f'Panel divider {i}')
  xf=sh.find('p:spPr/a:xfrm',ns)
  for key,val in [('x',x),('y',y)]:xf.find('a:off',ns).set(key,str(round(val*9525)))
  for key,val in [('cx',w),('cy',h)]:xf.find('a:ext',ns).set(key,str(round(val*9525)))
  sp.append(sh)
 parts[name]=E.tostring(t,xml_declaration=True,encoding='UTF-8',standalone=True)
for name in list(parts):
 if '/charts/' in name and name.endswith('.xml'):
  t=E.fromstring(parts[name])
  for ser in t.findall('.//c:lineChart/c:ser',ns):
   smooth=ser.find('c:smooth',ns)
   if smooth is None:smooth=E.SubElement(ser,'{'+ns['c']+'}smooth')
   smooth.set('val','0')
  parts[name]=E.tostring(t,xml_declaration=True,encoding='UTF-8',standalone=True)
with ZipFile(q/'polished_candidate.pptx','w',ZIP_DEFLATED) as z:
 for n,d in parts.items():z.writestr(n,d)
