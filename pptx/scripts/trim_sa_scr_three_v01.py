"""Keep the revised story and remove unreachable original-slide package parts."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as ET
import posixpath
ROOT=Path(__file__).resolve().parents[2];QA=ROOT/'pptx/qa/scr_three_v01'
P='http://schemas.openxmlformats.org/presentationml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
with ZipFile(QA/'body_untrimmed.pptx') as z:parts={n:z.read(n) for n in z.namelist()}
tree=ET.fromstring(parts['ppt/presentation.xml']);ids=tree.find('{'+P+'}sldIdLst')
remove={n.get('{'+R+'}id') for n in list(ids)[3:]}
for n in list(ids)[3:]:ids.remove(n)
rels=ET.fromstring(parts['ppt/_rels/presentation.xml.rels'])
for n in list(rels):
    if n.get('Id') in remove:rels.remove(n)
def xml(x):return ET.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
parts['ppt/presentation.xml']=xml(tree);parts['ppt/_rels/presentation.xml.rels']=xml(rels)
def relpath(part):return posixpath.join(posixpath.dirname(part),'_rels',posixpath.basename(part)+'.rels') if part else '_rels/.rels'
seen=set();todo=['']
while todo:
    part=todo.pop()
    if part in seen:continue
    seen.add(part)
    rp=relpath(part)
    if rp not in parts:continue
    seen.add(rp)
    for rel in ET.fromstring(parts[rp]):
        if rel.get('TargetMode')=='External':continue
        target=rel.get('Target');target=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(part),target))
        if target in parts:todo.append(target)
ct=ET.fromstring(parts['[Content_Types].xml'])
for n in list(ct):
    if n.tag.endswith('Override') and n.get('PartName').lstrip('/') not in seen:ct.remove(n)
parts['[Content_Types].xml']=xml(ct);seen.add('[Content_Types].xml')
with ZipFile(QA/'body.pptx','w',ZIP_DEFLATED) as z:
    for n in sorted(seen):
        if n in parts:z.writestr(n,parts[n])
print('Retained',len(ids),'slides; removed unreachable original content')
