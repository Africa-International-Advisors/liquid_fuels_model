"""Published group strategy and explicitly labelled African study implications."""
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_CONNECTOR


def draw_client_strategy(slide, brand, text):
    text(slide, 'Published group priorities | application to our study is our interpretation', .55, 1.8, 11.5, .35, 14)
    text(slide, 'What Vopak reports', 2.12, 2.43, 4.2, .3, 15, True)
    text(slide, 'What this means for the African study', 6.65, 2.43, 5.45, .3, 15, True)
    rows = [
        ('Improve', 'Improve financial and sustainability performance of existing assets. Target annual operating cash returns of 13–17%.',
         'South Africa: assess how changing national fuel flows affect terminal utilisation, handling demand, connectivity and operating performance.'),
        ('Grow', 'Prioritise gas and industrial terminals with attractive, long-term contracted returns. Group investment ambition: EUR 2.6bn through 2030.',
         'Walvis Bay / Namibia: test customer commitments, competing capacity and corridor access. Fuel deficits alone do not establish a viable terminal investment.'),
        ('Accelerate', 'Selective energy-transition investment: EUR 1.4bn ambition by 2030, including low-carbon fuels, sustainable feedstocks, ammonia and liquid CO2.',
         'Priority African markets: screen sustained service demand and transition compatibility. The agreed model scope remains petrol, diesel and jet.'),
    ]
    for i, (pillar, fact, implication) in enumerate(rows):
        y = 2.95 + i * 1.03
        text(slide, pillar, .55, y, 1.45, .32, 18, True, brand.accent_primary)
        text(slide, fact, 2.12, y, 4.17, .84, 13)
        text(slide, implication, 6.65, y, 5.45, .84, 13)
        rule = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(.55), Inches(y + .92), Inches(12.1), Inches(y + .92))
        rule.line.color.rgb = brand.grey_fill
        rule.line.width = Pt(.7)
    text(slide, 'The report provides group strategy; it does not set out a dedicated Africa expansion plan or a Walvis Bay investment commitment.', .55, 6.25, 11.5, .48, 13, True)
    text(slide, 'Commercial lens: sustained customer demand, usable infrastructure, contracted returns and investment requirements.', .55, 6.8, 11.5, .26, 11)
    credit = text(slide, 'Source: Royal Vopak, Half Year Report 2026, pp. 9, 11. African study implications are our analytical framing, not company commitments.', .5, 7.17, 10.1, .2, 8)
    for paragraph in credit.text_frame.paragraphs:
        for run in paragraph.runs:
            run.hyperlink.address = 'https://www.vopak.com/system/files/Half_Year_Report_2026_v2.pdf#page=11'
