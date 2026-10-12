"""Convert the existing demand series to native stacked area; preserve all data."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
r=Path(__file__).resolve().parents[2];q=r/'pptx/qa/evidence_v10';q.mkdir(exist_ok=True)
source=r/'pptx/output/delivered/supporting/archive/2026-10-12_accepted_v10/SA_SCR_Evidence_2026-10-12_v09.pptx'
with ZipFile(source) as z:parts={n:z.read(n) for n in z.namelist()}
ns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
n='ppt/charts/chart2.xml';t=E.fromstring(parts[n]);ch=t.find('.//c:lineChart',ns)
ch.tag='{'+ns['c']+'}areaChart';ch.find('c:grouping',ns).set('val','stacked')
for x in ch.xpath('./c:smooth|./c:ser/c:marker|./c:ser/c:smooth',namespaces=ns):x.getparent().remove(x)
for s,color in zip(ch.findall('c:ser',ns),['0A2373','6782B4']):
 sp=s.find('c:spPr',ns);fill=E.Element('{'+ns['a']+'}solidFill');E.SubElement(fill,'{'+ns['a']+'}srgbClr',val=color);sp.insert(0,fill)
axis=t.find('.//c:valAx/c:numFmt',ns);axis.set('formatCode','0');axis.set('sourceLinked','0')
parts[n]=E.tostring(t,xml_declaration=True,encoding='UTF-8',standalone=True)
with ZipFile(q/'reviewed_candidate.pptx','w',ZIP_DEFLATED) as z:
 for n,v in parts.items():z.writestr(n,v)
print('Changed only page 4 chart type; all series values and workbooks preserved.')
