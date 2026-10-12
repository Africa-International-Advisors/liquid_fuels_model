"""Apply the approved Vopak exhibit layout without rewriting data or chart parts.

Project extension for brand-pptx. See brand_configs/vopak_layout.json.
Usage: python pptx/scripts/lock_vopak_layout.py INPUT OUTPUT
"""
import argparse
import hashlib
import json
import posixpath
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E

ROOT = Path(__file__).resolve().parents[2]
NS = {'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
CFG = ROOT / 'pptx/brand_configs/vopak_layout.json'

def xml(b): return E.fromstring(b)
def serial(t): return E.tostring(t, xml_declaration=True, encoding='UTF-8', standalone=True)
def name(s):
    n=s.find('.//p:cNvPr',NS)
    return n.get('name','') if n is not None else ''
def text(s): return ''.join(s.itertext()) if False else ''.join(s.xpath('.//a:t/text()',namespaces=NS))
def box(s, values):
    xf=s.find('p:spPr/a:xfrm',NS)
    if xf is None: xf=s.find('p:xfrm',NS)
    if xf is None: raise ValueError('No transform: '+name(s))
    for key,val in zip(('x','y'),values[:2]): xf.find('a:off',NS).set(key,str(round(val*9525)))
    for key,val in zip(('cx','cy'),values[2:]): xf.find('a:ext',NS).set(key,str(round(val*9525)))
def font(s,size):
    for pr in s.xpath('.//a:rPr|.//a:defRPr|.//a:endParaRPr',namespaces=NS): pr.set('sz',str(round(size*75)))
def settext(s,value):
    ts=s.findall('.//a:t',NS)
    ts[0].text=value
    for t in ts[1:]: t.text=''
def readparts(path):
    with ZipFile(path) as z:return {n:z.read(n) for n in z.namelist()}

def apply(source, output):
    cfg=json.loads(CFG.read_text())
    ref=ROOT/cfg['reference']
    assert hashlib.sha256(ref.read_bytes()).hexdigest()==cfg['sha256'], 'Approved reference changed'
    rp=readparts(ref); parts=readparts(source)
    rt=xml(rp['ppt/slides/slide7.xml']).find('p:cSld/p:spTree',NS)
    refs={name(s):s for s in rt}
    markers=[s for s in rt if name(s).startswith('SCR divider marker')]
    # Register a named layout under the EXISTING supplied Vopak master.
    relname='ppt/slides/_rels/slide4.xml.rels'; rr=xml(parts[relname])
    lr=next(r for r in rr if r.get('Type').endswith('/slideLayout'))
    old=posixpath.normpath(posixpath.join('ppt/slides',lr.get('Target')))
    layout=xml(parts[old]);layout.set('matchingName',cfg['layout_name'])
    layout.find('p:cSld',NS).set('name',cfg['layout_name'])
    new='ppt/slideLayouts/slideLayoutVopakExhibitV1.xml'
    parts[new]=serial(layout)
    oldrels=posixpath.dirname(old)+'/_rels/'+posixpath.basename(old)+'.rels'
    newrels='ppt/slideLayouts/_rels/slideLayoutVopakExhibitV1.xml.rels'
    parts[newrels]=parts[oldrels]
    masterrel=next(r for r in xml(parts[oldrels]) if r.get('Type').endswith('/slideMaster'))
    master=posixpath.normpath(posixpath.join(posixpath.dirname(old),masterrel.get('Target')))
    mrname=posixpath.dirname(master)+'/_rels/'+posixpath.basename(master)+'.rels'
    mr=xml(parts[mrname]);rid='rIdVopakExhibitV1'
    E.SubElement(mr,'{'+REL+'}Relationship',Id=rid,Type=NS['r']+'/slideLayout',Target='../slideLayouts/'+posixpath.basename(new))
    parts[mrname]=serial(mr)
    mt=xml(parts[master]);lst=mt.find('p:sldLayoutIdLst',NS)
    lid=max(int(x.get('id')) for x in lst)+1
    E.SubElement(lst,'{'+NS['p']+'}sldLayoutId',id=str(lid),attrib={'{'+NS['r']+'}id':rid})
    parts[master]=serial(mt)
    ct=xml(parts['[Content_Types].xml'])
    E.SubElement(ct,'{'+CT+'}Override',PartName='/'+new,ContentType='application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml')
    parts['[Content_Types].xml']=serial(ct)
    for page in range(2,14):
        pn=f'ppt/slides/slide{page}.xml'; t=xml(parts[pn]);sp=t.find('p:cSld/p:spTree',NS)
        for s in list(sp):
            if name(s)=='brand-pptx section navigation' or name(s).startswith('Section navigation'):sp.remove(s)
        active=1 if page<=3 else 2 if page<=5 else 3 if page<=10 else 4
        ident=max(int(n.get('id')) for n in t.findall('.//p:cNvPr',NS))+1
        for s in sp:
            if name(s)=='Unified source footer':
                box(s,[48,681.6,979.2,24.96]);font(s,8)
        def add(s,n):
            nonlocal ident
            s=deepcopy(s);pr=s.find('.//p:cNvPr',NS);pr.set('id',str(ident));ident+=1;pr.set('name',n)
            for h in s.xpath('.//a:hlinkClick|.//a:hlinkMouseOver',namespaces=NS):h.getparent().remove(h)
            sp.append(s);return s
        for i in range(1,5):
            s=add(refs['Section navigation '+str(i)],'Section navigation '+str(i))
            style=refs['Section navigation '+str(3 if i==active else 1)]
            s.find('p:spPr/a:solidFill/a:srgbClr',NS).set('val','0A2373' if i==active else 'EEEEEE')
            ppr=s.find('p:txBody/a:p/a:pPr',NS);ppr.getparent().replace(ppr,deepcopy(style.find('p:txBody/a:p/a:pPr',NS)))
        if page in cfg['exhibit_pages']:
            by={name(s):s for s in sp}
            left='Evidence chart heading' if page<9 else 'Production history heading' if page==9 else 'Map heading'
            right='Evidence insight heading' if page<9 else 'Production implication' if page==9 else 'Map evidence heading'
            headings=[text(by[left]),text(by[right])]
            remove={left,right,'Evidence chart rule','Evidence insight rule','Evidence divider','Panel divider 0','Panel divider 1','Panel divider 2'}
            for s in list(sp):
                if name(s) in remove:sp.remove(s)
            for refn,newn,txt in [('TextBox 2800','Vopak exhibit left heading',headings[0]),('TextBox 3410','Vopak exhibit right heading',headings[1])]:
                s=add(refs[refn],newn);settext(s,txt)
            for refn,newn in [('Connector 2801','Vopak exhibit left rule'),('Connector 3420','Vopak exhibit right rule'),('Connector 3419','Vopak exhibit divider')]:add(refs[refn],newn)
            for i,s in enumerate(markers):add(s,'Vopak exhibit marker '+str(i))
            if page<9:
                box(by['Evidence unit'],[48,212,676.8,25])
                box(by['Evidence insights'],[779.52,235,386.88,330])
                box(by['Evidence takeaway'],[48,600,676.8,65]);font(by['Evidence takeaway'],17)
                for s in sp:
                    if s.find('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}chart') is not None:box(s,[48,245,676.8,310])
            elif page==9:
                box(by['Production units'],[48,212,676.8,25])
                box(by['Production assumption'],[779.52,230,386.88,56])
                box(by['Production commentary'],[779.52,300,386.88,320])
                box(by['Production events'],[48,565,676.8,90]);font(by['Production events'],16)
                for s in sp:
                    if s.find('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}chart') is not None:box(s,[48,245,676.8,300])
            else:
                # Preserve the existing map crop and aspect ratio inside the left panel.
                for s in sp:
                    if s.tag=='{'+NS['p']+'}pic':box(s,[91.4,230,590,365.0133])
                box(by['Map scope'],[48,605,676.8,58]);font(by['Map scope'],15)
                for i in range(5):
                    box(by['Route heading '+str(i)],[779.52,225+i*86,386.88,26]);font(by['Route heading '+str(i)],17)
                    box(by['Route body '+str(i)],[779.52,251+i*86,386.88,64]);font(by['Route body '+str(i)],15)
            rn=f'ppt/slides/_rels/slide{page}.xml.rels';rr=xml(parts[rn])
            next(r for r in rr if r.get('Type').endswith('/slideLayout')).set('Target','../slideLayouts/'+posixpath.basename(new))
            parts[rn]=serial(rr)
        parts[pn]=serial(t)
    # No chart / embedded workbook is modified by this layout operation.
    original=readparts(source)
    assert all(parts[n]==v for n,v in original.items() if '/charts/' in n or '/embeddings/' in n)
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():raise FileExistsError(output)
    with ZipFile(output,'w',ZIP_DEFLATED) as z:
        for n,b in parts.items():z.writestr(n,b)
    check(output)

def check(path, profile=None):
    cfg=json.loads(CFG.read_text());parts=readparts(path)
    ref=readparts(ROOT/cfg['reference']);rt=xml(ref['ppt/slides/slide7.xml'])
    refs={name(s):s for s in rt.find('p:cSld/p:spTree',NS)}
    pairs={'Vopak exhibit left heading':'TextBox 2800','Vopak exhibit right heading':'TextBox 3410','Vopak exhibit left rule':'Connector 2801','Vopak exhibit right rule':'Connector 3420','Vopak exhibit divider':'Connector 3419'}
    scope=cfg.get('deck_profiles',{}).get(profile,{})
    for page in scope.get('navigation_pages',list(range(2,14))):
        t=xml(parts[f'ppt/slides/slide{page}.xml']);by={name(s):s for s in t.find('p:cSld/p:spTree',NS)}
        for i in range(1,5):assert text(by['Section navigation '+str(i)])==text(refs['Section navigation '+str(i)])
        if page not in scope.get('exhibit_pages',cfg['exhibit_pages']):continue
        for n,r in pairs.items():
            for component in ['a:off','a:ext']:
                assert by[n].find('p:spPr/a:xfrm/'+component,NS).attrib==refs[r].find('p:spPr/a:xfrm/'+component,NS).attrib,(page,n)
        assert sum(n.startswith('Vopak exhibit marker ') for n in by)==3
        for n in ['Vopak exhibit left heading','Vopak exhibit right heading']:
            assert by[n].find('.//a:defRPr/a:solidFill/a:srgbClr',NS).get('val')=='000000'
        rr=xml(parts[f'ppt/slides/_rels/slide{page}.xml.rels'])
        rel=next(r for r in rr if r.get('Type').endswith('/slideLayout'))
        target=posixpath.normpath(posixpath.join('ppt/slides',rel.get('Target')))
        assert xml(parts[target]).find('p:cSld',NS).get('name')==cfg['layout_name']
    print('PASS: approved navigation, exhibit geometry, headings, markers and named layout')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path,nargs='?');p.add_argument('--check',action='store_true');p.add_argument('--profile');a=p.parse_args()
    if a.check:check(a.input,a.profile)
    else:apply(a.input,a.output)
