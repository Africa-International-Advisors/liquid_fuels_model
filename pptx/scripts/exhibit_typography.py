"""Shared font sizes for comparable analytical exhibits."""
from pptx.util import Pt, Inches

CHART_LABEL = 12
CHART_SECONDARY = 11
MAP_CALLOUT = 11
LEGEND = 11


def standardise_reused_map_callouts(s):
    """Apply the current hierarchy to preserved cost-map labels without rebuilding tiles."""
    for q in s.shapes:
        if not q.has_text_frame: continue
        value = q.text
        if value.startswith(('Inland market | illustrative','Eastern/coastal | illustrative')):
            q.width = Inches(3.0); q.height = Inches(.84)
            if value.startswith('Eastern/coastal'): q.left = Inches(4.54)
            for p in q.text_frame.paragraphs: p.font.size = Pt(MAP_CALLOUT)
        elif value in ('Durban','Lesedi*'):
            q.height = Inches(.29)
            for p in q.text_frame.paragraphs: p.font.size = Pt(MAP_CALLOUT)

        elif value in ('≤0.75','0.75–1.25','1.25–1.75','1.75–2.25','>2.25','Unassessed'):
            q.top = Inches(6.44); q.height = Inches(.26)
            if value == 'Unassessed': q.width = Inches(1.35)
            for p in q.text_frame.paragraphs: p.font.size = Pt(LEGEND)
        elif value == 'R/litre' and q.top > Inches(6):
            q._element.getparent().remove(q._element)
        elif value == 'Cost accessibility and market volumes | illustrative':
            q.text_frame.paragraphs[0].runs[0].text = 'Illustrative road cost (R/litre) and market volumes'
