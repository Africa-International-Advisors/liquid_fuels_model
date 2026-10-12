"""Replace inherited internal cover notes with a client-facing description."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
r=Path(__file__).resolve().parents[2];q=r/'pptx/qa/story_v37'
with ZipFile(q/'with_chart_workbooks.pptx') as source,ZipFile(q/'client_candidate.pptx','w',ZIP_DEFLATED) as target:
 for name in source.namelist():
  data=source.read(name)
  if name=='ppt/notesSlides/notesSlide1.xml':
   t=E.fromstring(data)
   texts=t.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}t')
   for i,n in enumerate(texts):n.text='South Africa fuel-market analysis. Sources and assumptions appear on the relevant analytical pages.' if i==0 else ''
   data=E.tostring(t,encoding='UTF-8',xml_declaration=True,standalone=True)
  target.writestr(name,data)
