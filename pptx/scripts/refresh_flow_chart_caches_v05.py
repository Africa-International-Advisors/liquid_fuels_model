from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from io import BytesIO
from lxml import etree as E
import posixpath,re
r=Path(__file__).resolve().parents[2];q=r/'pptx/qa/evidence_v05'
ns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with ZipFile(q/'SA_SCR_Evidence_2026-10-12_v05.pptx') as z:parts={n:z.read(n) for n in z.namelist()}
for name,data in list(parts.items()):
 if '/charts/chart' not in name or not name.endswith('.xml'):continue
 tree=E.fromstring(data);ext=tree.find('.//c:externalData',ns)
 if ext is None:continue
 rels=E.fromstring(parts[posixpath.join(posixpath.dirname(name),'_rels',posixpath.basename(name)+'.rels')])
 rel=next(n for n in rels if n.get('Id')==ext.get('{'+ns['r']+'}id'))
 target=rel.get('Target');book=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(name),target))
 with ZipFile(BytesIO(parts[book])) as wb:
  cells={n.get('r'):n.find('x:v',ns).text for n in E.fromstring(wb.read('xl/worksheets/sheet1.xml')).findall('.//x:c',ns) if n.find('x:v',ns) is not None}
 for ref in tree.findall('.//c:numRef',ns):
  f=ref.find('c:f',ns).text;span=f.split('!')[-1].replace('$','');start=span.split(':')[0]
  col,row=re.fullmatch(r'([A-Z]+)(\d+)',start).groups()
  for pt in ref.findall('c:numCache/c:pt',ns):pt.find('c:v',ns).text=cells[f'{col}{int(row)+int(pt.get("idx"))}']
 parts[name]=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
with ZipFile(q/'refreshed_candidate.pptx','w',ZIP_DEFLATED) as z:
 for n,d in parts.items():z.writestr(n,d)
print('Refreshed chart caches from unchanged embedded workbook cells')
