from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
r=Path(__file__).resolve().parents[2];q=r/'pptx/qa/evidence_v04'
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
replacements={
 'Sector activity':'Sector activity | p5',
 'Eskom recovery':'Eskom recovery | p6',
 'Road-to-rail':'Road-to-rail | p7',
 'Vehicle efficiency':'Vehicle efficiency | p8',
 'Refinery output and restarts':'Refinery output and restarts | p9',
 'Ports and inland connections':'Ports and inland connections | p10',
 'Observed use and estimated scope':'Power fuel use',
}
with ZipFile(q/'with_chart_workbooks.pptx') as z,ZipFile(q/'reviewed_candidate.pptx','w',ZIP_DEFLATED) as out:
 for item in z.infolist():
  data=z.read(item.filename)
  if item.filename in ['ppt/slides/slide3.xml','ppt/slides/slide6.xml']:
   tree=E.fromstring(data)
   for n in tree.findall('.//a:t',ns):
    if n.text in replacements:n.text=replacements[n.text]
    elif n.text and 'Detailed evidence: South Africa story v37 pp7' in n.text:
     n.text='Demand baseline: p4. Driver evidence: pp5–10. Stats SA; Eskom Integrated Report 2025 p141; Sasol, Glencore, Galp and Petromoc disclosures; naamsa vehicle sales.'
   data=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
  out.writestr(item,data)
