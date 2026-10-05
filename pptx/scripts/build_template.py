"""Create the user-requested Vopak template revision; never modify the original."""
from pathlib import Path
from copy import deepcopy
import sys
from lxml import etree
from pptx import Presentation
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from brand_pptx import pptx_to_potx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from brand_configs import vopak as cfg

prs = Presentation(ROOT / 'templates/AIA_Vopak_Template.pptx')
master = prs.slide_masters[0]
cover = next(l for l in prs.slide_layouts if l.name == '1_Title')
aia = {s.image.sha1 for owner, name in [(master, 'Picture 4'), (cover, 'Picture 5')]
       for s in owner.shapes if s.shape_type == 13 and s.name == name}
logo = next(s for s in prs.slides[0].shapes if s.shape_type == 13)
logo_xml = deepcopy(logo._element)
logo_part = logo.part.related_part(logo._element.blipFill.blip.rEmbed)

for owner in [master, *master.slide_layouts, *prs.slides]:
    for s in list(owner.shapes):
        if (s.shape_type == 13 and s.image.sha1 in aia) or (
            s.shape_type == 1 and s.width < Inches(.15) and abs(s.left) < Inches(.05)):
            s._element.getparent().remove(s._element)
            continue
        if owner == master and s.shape_type == 13 and s.name == 'Picture 2':
            ratio = s.height / s.width
            s.width = Inches(.85)
            s.height = int(s.width * ratio)
            s.left, s.top = Inches(11.05), Inches(7.17)
        if getattr(owner, 'name', '') == 'Header only' and s.is_placeholder and s.placeholder_format.idx == 0:
            s.left, s.top, s.width, s.height = Inches(.5), Inches(.64), Inches(11.55), Inches(.9)
        if s.has_text_frame:
            for props in s._element.xpath('.//a:rPr | .//a:defRPr | .//a:endParaRPr'):
                for child in list(props):
                    if etree.QName(child).localname in ('solidFill','gradFill','noFill'):
                        props.remove(child)
                fill = OxmlElement('a:solidFill')
                color = OxmlElement('a:schemeClr'); color.set('val','tx1')
                fill.append(color); props.insert(0, fill)
    if owner in list(master.slide_layouts) and owner.name in ('1_Title','2_Title'):
        temporary = prs.slides[1].shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(.13), Inches(5.13), Inches(5.46), Inches(2.18))
        temporary.fill.solid()
        temporary.fill.fore_color.rgb = RGBColor.from_string('E7E6E6')
        temporary.line.fill.background()
        color = temporary._element.spPr.xpath('./a:solidFill/a:srgbClr')[0]
        alpha = OxmlElement('a:alpha'); alpha.set('val', '60000'); color.append(alpha)
        panel = deepcopy(temporary._element)
        panel.xpath('.//p:cNvPr')[0].set('id', str(max(s.shape_id for s in owner.shapes)+1))
        panel.xpath('.//p:cNvPr')[0].set('name', 'Cover title panel')
        owner.shapes._spTree.insert_element_before(panel, 'p:extLst')
        temporary._element.getparent().remove(temporary._element)
        copied = deepcopy(logo_xml)
        copied.xpath('.//p:cNvPr')[0].set('id', str(max(s.shape_id for s in owner.shapes)+1))
        copied.xpath('.//p:cNvPr')[0].set('name', 'Vopak cover logo')
        copied.blipFill.blip.rEmbed = owner.part.relate_to(logo_part, RT.IMAGE)
        owner.shapes._spTree.insert_element_before(copied, 'p:extLst')

# The cover logo now belongs to its reusable layout rather than a sample slide.
logo._element.getparent().remove(logo._element)
prs.slides[0].shapes[0].fill.background()
prs.slides[0].shapes[0].text = 'Presentation title\nSubtitle\nDate'
for slide in list(prs.slides)[1:]:
    for s in slide.shapes:
        if s.has_text_frame:
            s.text = 'Slide title' if s.is_placeholder and s.placeholder_format.idx == 0 else ''
for s in master.shapes:
    if s.name == 'Text Placeholder 6':
        s.left, s.top, s.width, s.height = Inches(.5), Inches(7.14), Inches(9.4), Inches(.25)
        s.text = 'Source: [insert source]'
        s.text_frame.margin_top = s.text_frame.margin_bottom = 0
        for p in s.text_frame.paragraphs:
            p.font.name = cfg.THEME_FONT
            p.font.size = Pt(8)
            p.font.color.rgb = RGBColor.from_string('404040')
line = prs.slides[1].shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(.5), Inches(7.04), Inches(12.15), Inches(7.04))
line.line.width = Pt(.25)
line.line.color.rgb = cfg.DIVIDER_FRAME
line.name = 'Fine footer rule'
line_xml = deepcopy(line._element)
line_xml.xpath('.//p:cNvPr')[0].set('id', str(max(s.shape_id for s in master.shapes)+1))
master.shapes._spTree.insert_element_before(line_xml, 'p:extLst')
line._element.getparent().remove(line._element)
header = next(l for l in master.slide_layouts if l.name == 'Header only')
line = prs.slides[1].shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(.5), Inches(1.58), Inches(12.15), Inches(1.58))
line.line.width = Pt(.25)
line.line.color.rgb = cfg.DIVIDER_FRAME
line.name = 'Title and body separator'
line_xml = deepcopy(line._element)
line_xml.xpath('.//p:cNvPr')[0].set('id', str(max(s.shape_id for s in header.shapes)+1))
header.shapes._spTree.insert_element_before(line_xml, 'p:extLst')
line._element.getparent().remove(line._element)
for props in master._element.xpath('./p:txStyles//a:defRPr'):
    for fill in props.xpath('./a:solidFill'):
        for child in list(fill): fill.remove(child)
        color = OxmlElement('a:schemeClr'); color.set('val','tx1'); fill.append(color)
for rel in master.part.rels.values():
    if rel.reltype.endswith('/theme'):
        theme = etree.fromstring(rel.target_part.blob)
        ns = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
        scheme = theme.find('.//a:clrScheme',ns)
        for slot, value in cfg.THEME_COLOURS.items():
            node = scheme.find('a:'+slot,ns)
            for child in list(node): node.remove(child)
            color = OxmlElement('a:srgbClr'); color.set('val',value); node.append(color)
        rel.target_part._blob = etree.tostring(theme,encoding='UTF-8',xml_declaration=True,standalone=True)
prs.core_properties.title = 'Vopak presentation template v2'
prs.core_properties.subject = 'Black text, Vopak blue accents, Vopak-only logos, clean titles'
destination = ROOT / cfg.SOURCE_TEMPLATE
prs.save(destination)
pptx_to_potx(destination, destination.with_suffix('.potx'))
print(destination)
