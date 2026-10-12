"""Apply package Marvin rules to native tables and straight annual chart lines."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import re
r=Path(__file__).resolve().parents[2];q=r/'pptx/qa/story_v37'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
C='http://schemas.openxmlformats.org/drawingml/2006/chart'
ns={'a':A,'c':C}
with ZipFile(q/'body.pptx') as z,ZipFile(q/'styled_body.pptx','w',ZIP_DEFLATED) as out:
 for name in z.namelist():
  data=z.read(name)
  if name.endswith('.xml'):
   data=data.replace(b'User direction 11 October 2026.',b'National production planning assumption.').replace(b'national planning assumption',b'National planning assumption')
  if name.startswith('ppt/slides/slide') and name.endswith('.xml'):
   tree=E.fromstring(data)
   for table in tree.findall('.//a:tbl',ns):
    for n in table.findall('a:tblPr/a:tableStyleId',ns):n.getparent().remove(n)
    trs=table.findall('a:tr',ns)
    numeric=lambda text:bool(re.fullmatch(r'-?[\d,.]+(?:%|bn litres)?',text.strip()))
    right_columns=set()
    if len(trs)>1:
     for ci in range(1,len(trs[0].findall('a:tc',ns))):
      if all(numeric(''.join(row.findall('a:tc',ns)[ci].itertext())) for row in trs[1:]):right_columns.add(ci)
    for ri,tr in enumerate(trs):
     for ci,tc in enumerate(tr.findall('a:tc',ns)):
      pr=tc.find('a:tcPr',ns)
      if pr is None:pr=E.SubElement(tc,'{'+A+'}tcPr')
      for n in list(pr):
       if E.QName(n).localname.startswith('ln') or E.QName(n).localname.endswith('Fill'):pr.remove(n)
      for side in ['L','R','T','B']:
       ln=E.SubElement(pr,'{'+A+'}ln'+side,w='12700' if ri==0 else '6350')
       if side=='B':
        fill=E.SubElement(ln,'{'+A+'}solidFill');E.SubElement(fill,'{'+A+'}srgbClr',val='666666' if ri==0 else 'D0D0D0')
       else:E.SubElement(ln,'{'+A+'}noFill')
      fill=E.SubElement(pr,'{'+A+'}solidFill');E.SubElement(fill,'{'+A+'}srgbClr',val='FFFFFF')
      for color in tc.findall('.//a:rPr/a:solidFill/a:srgbClr',ns):color.set('val','11151A')
      text=''.join(tc.itertext()).strip()
      if ci in right_columns or (ci>0 and numeric(text)):
       for p in tc.findall('a:txBody/a:p',ns):
        pp=p.find('a:pPr',ns)
        if pp is None:pp=E.Element('{'+A+'}pPr');p.insert(0,pp)
        pp.set('algn','r')
   data=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
  if '/charts/' in name and name.endswith('.xml'):
   tree=E.fromstring(data)
   for ser in tree.findall('.//c:lineChart/c:ser',ns):
    smooth=ser.find('c:smooth',ns)
    if smooth is None:smooth=E.SubElement(ser,'{'+C+'}smooth')
    smooth.set('val','0')
   data=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
  out.writestr(name,data)
print('Applied white Marvin tables, horizontal rules and right-aligned numbers')
