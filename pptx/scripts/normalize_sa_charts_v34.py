"""Restore Excel precision after PowerPoint serialises numeric caches."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as ET
root=Path(__file__).resolve().parents[2]
qa=root/'pptx/qa/story_v34'
ns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
with ZipFile(qa/'SA_Market_Story_2026-10-11_v34.pptx') as zin, ZipFile(qa/'normalized.pptx','w',ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data=zin.read(item.filename)
        if '/charts/' in item.filename and item.filename.endswith('.xml'):
            tree=ET.fromstring(data)
            for value in tree.xpath('//c:numCache/c:pt/c:v',namespaces=ns):
                value.text=format(float(value.text),'.15g')
            data=ET.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
        zout.writestr(item,data)
