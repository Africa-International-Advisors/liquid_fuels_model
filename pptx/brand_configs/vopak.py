"""Vopak settings extracted from the supplied, unchanged corporate template.

Paths resolve from the pptx project directory. Primary blue matches the supplied
Vopak logo (dominant opaque pixel #0A2373), as requested by the user.
"""
from pathlib import Path
from pptx.dml.color import RGBColor

DIVIDER_HEADER = RGBColor.from_string('A0A0A0')
DIVIDER_BODY = RGBColor.from_string('B8B8B8')
DIVIDER_FRAME = RGBColor.from_string('B0B0B0')

# Geographic scope: progressively lighter tints of the Vopak logo blue.
MAP_REGION_COLOURS = {
    'SACU': RGBColor.from_string('0A2373'),
    'SADC excluding SACU': RGBColor.from_string('536598'),
    'East Africa': RGBColor.from_string('8491B2'),
    'West Africa': RGBColor.from_string('AAB3CE'),
    'North Africa': RGBColor.from_string('CED3E3'),
    'Central Africa': RGBColor.from_string('BFC7DE'),
}

BRAND_NAME = "Vopak"
SOURCE_TEMPLATE = Path("templates/Vopak_Template_v2.pptx")
TEMPLATE_PPTX = Path("output/templates/vopak.pptx")
TEMPLATE_POTX = Path("output/templates/vopak.potx")
THEME_FONT = "Lato"
THEME_COLOURS = {
    "dk1": "000000", "lt1": "FFFFFF", "dk2": "11151A", "lt2": "E7E6E6",
    "accent1": "0A2373", "accent2": "546CA2", "accent3": "BDBEC1",
    "accent4": "404040", "accent5": "767676", "accent6": "D9D9D9",
    "hlink": "0A2373", "folHlink": "546CA2",
}
IMAGE_REPLACEMENTS = {}
STRIP_SAMPLE_SLIDES = True
STRIP_RECENT_COLORS = True
AUTHOR = "Africa International Advisors"
COMPANY = "Africa International Advisors"
