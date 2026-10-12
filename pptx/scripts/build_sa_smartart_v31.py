"""Apply brand-pptx native SmartArt navigation using desktop PowerPoint.

No presentation body or analytical data is authored by this script.
"""
from pathlib import Path
import json
import time
import pythoncom
import win32com.client
from brand_pptx import BrandStyle, restyle_smartart_navigation
from brand_pptx.navigation import CHEVRON_LAYOUT_ID, _rgb
from pptx.dml.color import RGBColor

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / 'pptx/qa/smartart_v31'
QA.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'pptx/output/delivered/supporting/archive/2026-10-11_cleanup/SA_Market_Story_2026-10-10_v30.pptx'
OUTPUT = QA / 'SA_Market_Story_2026-10-10_v31.pptx'
if OUTPUT.exists():
    raise FileExistsError(OUTPUT)

# Match the supplied Vopak brand config and the deck's navigation palette.
brand = BrandStyle(font='Lato', accent_primary=RGBColor.from_string('0A2373'),
                   accent_highlight=RGBColor.from_string('0A2373'),
                   ink=RGBColor.from_string('0A2373'),
                   grey_fill=RGBColor.from_string('F5F5F5'))
app = win32com.client.Dispatch('PowerPoint.Application')
deck = app.Presentations.Open(str(SOURCE), ReadOnly=True, Untitled=False, WithWindow=False)
clean = QA / 'without_custom_navigation.pptx'
removed = 0
try:
    for slide in deck.Slides:
        for i in range(slide.Shapes.Count, 0, -1):
            if slide.Shapes.Item(i).Name in ('SCR 1', 'SCR 2', 'SCR 3', 'SCR 4'):
                slide.Shapes.Item(i).Delete()
                removed += 1
    deck.SaveAs(str(clean), 24)
finally:
    deck.Close()
print(f'Removed {removed} custom rectangles', flush=True)
main = {n: (0 if n <= 7 else 1 if n <= 13 else 2 if n <= 17 else 3) for n in range(2,20)}
appendix = {n: (0 if n == 21 else 1 if n <= 31 else 2 if n <= 38 else 3) for n in range(21,45)}
geometry = dict(left=.5, top=.09, width=11.65, height=.31, font_size=10.5, numbered=False)
# Create eight native Office SmartArt variants in small saved presentations.
# Transplant their complete diagram parts into the deck, then apply the package
# restyler. Small batches avoid this workstation's unstable repeated paste API.
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as ET
import posixpath
xl = win32com.client.Dispatch('Excel.Application')
book = xl.Workbooks.Add()
variants = {}
try:
    layout = xl.SmartArtLayouts.Item(CHEVRON_LAYOUT_ID)
    for group,labels,mapping in [('main',['Executive summary','Situation','Complication','Resolution'],main),
                                 ('appendix',['Appendix','Supporting evidence','Calibration','Reference detail'],appendix)]:
        for active in sorted(set(mapping.values())):
            saved = QA / f'component_{group}_{active}.pptx'
            variants[(group,active)] = saved
            if saved.exists(): continue
            nav=book.Worksheets.Item(1).Shapes.AddSmartArt(layout,36,6.48,838.8,22.32)
            nav.SmartArt.AllNodes.Item(3).AddNode(2,1)
            for i,label in enumerate(labels):
                node=nav.SmartArt.AllNodes.Item(i+1)
                node.TextFrame2.TextRange.Text=label
                node.TextFrame2.TextRange.Font.Name=brand.font
                node.TextFrame2.TextRange.Font.Size=10.5
                node.TextFrame2.TextRange.Font.Bold=-1 if i==active else 0
                node.TextFrame2.TextRange.Font.Fill.ForeColor.RGB=_rgb(brand.white if i==active else brand.ink)
                for j in range(1,node.Shapes.Count+1):
                    part=node.Shapes.Item(j)
                    part.Fill.Solid()
                    part.Fill.ForeColor.RGB=_rgb(brand.accent_highlight if i==active else brand.grey_fill)
                    part.Line.Visible=0
                    part.Shadow.Visible=0
            deck=app.Presentations.Open(str(clean),ReadOnly=True,Untitled=False,WithWindow=False)
            try:
                nav.Copy()
                time.sleep(1)
                pasted=deck.Slides.Item(2).Shapes.Paste().Item(1)
                pasted.Name='brand-pptx section navigation'
                pasted.Left,pasted.Top,pasted.Width,pasted.Height=36,6.48,838.8,22.32
                if not pasted.HasSmartArt: raise RuntimeError('SmartArt lost during paste')
                time.sleep(1)
                deck.SaveAs(str(saved),24)
            finally:
                deck.Close()
            nav.Delete()
            print(f'Saved native component {group}/{active}',flush=True)
finally:
    book.Close(False)

NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel':'http://schemas.openxmlformats.org/package/2006/relationships',
    'ct':'http://schemas.openxmlformats.org/package/2006/content-types'}
with ZipFile(clean) as z: parts={n:z.read(n) for n in z.namelist()}
ct=ET.fromstring(parts['[Content_Types].xml'])
def xml(x): return ET.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
def relpath(part): return posixpath.join(posixpath.dirname(part),'_rels',posixpath.basename(part)+'.rels')
for group,mapping in [('main',main),('appendix',appendix)]:
    for page,active in mapping.items():
        with ZipFile(variants[(group,active)]) as z: src={n:z.read(n) for n in z.namelist()}
        source_slide=ET.fromstring(src['ppt/slides/slide2.xml'])
        frame=next(f for f in source_slide.findall('.//p:graphicFrame',NS)
                   if f.find('p:nvGraphicFramePr/p:cNvPr',NS).get('name')=='brand-pptx section navigation')
        src_rels=ET.fromstring(src['ppt/slides/_rels/slide2.xml.rels'])
        src_types={n.get('PartName').lstrip('/'):n.get('ContentType') for n in ET.fromstring(src['[Content_Types].xml']) if n.tag.endswith('Override')}
        copied={}
        def copy_part(old):
            if old in copied: return copied[old]
            new=posixpath.join(posixpath.dirname(old),f'v31_s{page}_'+posixpath.basename(old))
            copied[old]=new
            parts[new]=src[old]
            if old in src_types: ET.SubElement(ct,'{'+NS['ct']+'}Override',PartName='/'+new,ContentType=src_types[old])
            old_rels=relpath(old)
            if old_rels in src:
                tree=ET.fromstring(src[old_rels])
                for rel in tree:
                    if rel.get('TargetMode')=='External': continue
                    target=rel.get('Target')
                    absolute=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(old),target))
                    copied_target=copy_part(absolute)
                    rel.set('Target',posixpath.relpath(copied_target,posixpath.dirname(new)))
                parts[relpath(new)]=xml(tree)
            return new
        target_slide=f'ppt/slides/slide{page}.xml'
        target_rels=relpath(target_slide)
        rels=ET.fromstring(parts[target_rels])
        used={n.get('Id') for n in rels}
        for node in frame.iter():
            for attr,value in list(node.attrib.items()):
                if not attr.startswith('{'+NS['r']+'}'): continue
                source_rel=next(n for n in src_rels if n.get('Id')==value)
                target=source_rel.get('Target')
                absolute=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('ppt/slides',target))
                newpart=copy_part(absolute)
                newid=f'rIdSmartArt{len(used)+1}'
                while newid in used: newid+='x'
                used.add(newid)
                ET.SubElement(rels,'{'+NS['rel']+'}Relationship',Id=newid,Type=source_rel.get('Type'),Target=posixpath.relpath(newpart,'ppt/slides'))
                node.set(attr,newid)
        # Office stores the cached drawing relation in dataModelExt, referring
        # back to a slide relationship rather than a data-part relationship.
        for oldpart,newpart in list(copied.items()):
            if 'data' not in posixpath.basename(oldpart): continue
            data_tree=ET.fromstring(parts[newpart])
            for extension in data_tree.iter():
                oldid=extension.get('relId')
                if not oldid: continue
                source_rel=next((n for n in src_rels if n.get('Id')==oldid and n.get('Type','').endswith('/diagramDrawing')),None)
                if source_rel is None: continue
                target=source_rel.get('Target')
                absolute=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('ppt/slides',target))
                drawing=copy_part(absolute)
                newid=f'rIdV31Drawing{page}'
                ET.SubElement(rels,'{'+NS['rel']+'}Relationship',Id=newid,Type=source_rel.get('Type'),Target=posixpath.relpath(drawing,'ppt/slides'))
                extension.set('relId',newid)
            parts[newpart]=xml(data_tree)
        frame.find('p:nvGraphicFramePr/p:cNvPr',NS).set('id',str(5000+page))
        tree=ET.fromstring(parts[target_slide])
        tree.find('p:cSld/p:spTree',NS).append(frame)
        parts[target_slide]=xml(tree)
        parts[target_rels]=xml(rels)
parts['[Content_Types].xml']=xml(ct)
native_raw=QA/'native_before_package_style.pptx'
with ZipFile(native_raw,'w',ZIP_DEFLATED) as z:
    for name,data in parts.items():z.writestr(name,data)
restyle_smartart_navigation(native_raw,OUTPUT,left=.5,top=.09,width=11.65,height=.31,font_size=10.5,gap=.06)
print('Package SmartArt styling complete',flush=True)

render = QA / 'powerpoint_render'
render.mkdir(exist_ok=True)
deck = app.Presentations.Open(str(OUTPUT), ReadOnly=True, Untitled=False, WithWindow=False)
native = []
try:
    for slide in deck.Slides:
        for s in slide.Shapes:
            if s.Name == 'brand-pptx section navigation':
                native.append({'page': slide.SlideIndex, 'has_smartart': bool(s.HasSmartArt),
                               'nodes': s.SmartArt.AllNodes.Count})
    deck.SaveAs(str(OUTPUT.with_suffix('.pdf')),32)
    deck.Export(str(render), 'PNG',1217,720)
finally:
    deck.Close()
if len(native) != 42 or not all(x['has_smartart'] and x['nodes']==4 for x in native):
    raise RuntimeError('Native SmartArt inventory does not match 42 four-section bars')
(QA/'navigation_record.json').write_text(json.dumps({'removed':removed,'native':native,
    'main_active':main,'appendix_active':appendix},indent=2),encoding='utf8')
print('Exported 44 slides; verified 42 native SmartArt bars', flush=True)
