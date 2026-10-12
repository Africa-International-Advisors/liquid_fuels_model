"""Attach preserved package-native SmartArt components to the restructured deck."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as ET
import posixpath
import json
import win32com.client
from brand_pptx import restyle_smartart_navigation
ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'pptx/qa/scr_six_v03'
clean=QA/'styled_body.pptx'
OUTPUT=QA/'SA_SCR_Six_Page_2026-10-11_v03.pptx'
meta=json.loads((QA/'page_map.json').read_text())
main={int(k):v for k,v in meta['nav']['main'].items()}
appendix={int(k):v for k,v in meta['nav']['appendix'].items()}
variants={(g,i):ROOT/f'pptx/qa/smartart_v31/component_{g}_{i}.pptx' for g in ['main','appendix'] for i in range(4)}
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
            new=posixpath.join(posixpath.dirname(old),f'v32_s{page}_'+posixpath.basename(old))
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
                newid=f'rIdV32Drawing{page}'
                ET.SubElement(rels,'{'+NS['rel']+'}Relationship',Id=newid,Type=source_rel.get('Type'),Target=posixpath.relpath(drawing,'ppt/slides'))
                extension.set('relId',newid)
            parts[newpart]=xml(data_tree)
        frame.find('p:nvGraphicFramePr/p:cNvPr',NS).set('id',str(5000+page))
        tree=ET.fromstring(parts[target_slide])
        tree.find('p:cSld/p:spTree',NS).append(frame)
        parts[target_slide]=xml(tree)
        parts[target_rels]=xml(rels)
for part_name in list(parts):
    if part_name.startswith('ppt/slides/slide') and part_name.endswith('.xml'):
        parts[part_name] = parts[part_name].replace(
            b'The following page presents the current analytical response.',
            b'Pages 2-18 present the current analytical response.')
parts['[Content_Types].xml']=xml(ct)
native_raw=QA/'native_before_package_style.pptx'
with ZipFile(native_raw,'w',ZIP_DEFLATED) as z:
    for name,data in parts.items():z.writestr(name,data)
restyle_smartart_navigation(native_raw,OUTPUT,left=.5,top=.09,width=11.65,height=.31,font_size=10.5,gap=.06)
print('Package SmartArt styling complete',flush=True)

render=QA/'powerpoint_render'
render.mkdir(exist_ok=True)
app=win32com.client.Dispatch('PowerPoint.Application')
deck=app.Presentations.Open(str(OUTPUT),ReadOnly=True,Untitled=False,WithWindow=False)
native=[]
try:
    for slide in deck.Slides:
        for shape in slide.Shapes:
            if shape.Name=='brand-pptx section navigation':
                native.append({'page':slide.SlideIndex,'native':bool(shape.HasSmartArt),'nodes':shape.SmartArt.AllNodes.Count})
    deck.SaveAs(str(OUTPUT.with_suffix('.pdf')),32)
    deck.Export(str(render),'PNG',1217,720)
finally:
    deck.Close()
assert len(native)==4 and all(v['native'] and v['nodes']==4 for v in native)
(QA/'navigation_record.json').write_text(json.dumps(native,indent=2))
print('Exported 6 slides; 4 native SmartArt navigation bars',flush=True)
