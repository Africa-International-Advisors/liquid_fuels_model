"""Render a declared reporting illustration; no investment model is executed."""
from pptx.util import Inches, Pt
from pptx.enum.chart import XL_CHART_TYPE, XL_DATA_LABEL_POSITION
from brand_pptx import add_themed_chart
from brand_configs import vopak as cfg
from supply_review_pages import read, frame


def add_storage_sensitivity_page(s, text, root, brand):
    rows = read(root/'story/storage_inventory_sensitivity_2026_10_06.csv')
    frame(s, 'Translate additional fuel flows into a preliminary inventory requirement',
          'Working inventory sensitivity | illustrative, thousand m³',
          'Existing 5.5 bn L/year candidate example; authored inventory-day sensitivity, 6 Oct 2026. Not new-capacity sizing.', text, brand)
    text(s, 'ILLUSTRATIVE | additional 5.5 bn litres/year; uniform daily flow',
         .5, 2.35, 7.05, .30, 11, True, brand.accent_primary)
    text(s, 'More inventory days require more working stock', .5, 2.83, 7.05, .32, 14, True, brand.accent_primary)
    chart = add_themed_chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED,
        Inches(.5), Inches(3.29), Inches(7.05), Inches(2.56),
        [r['inventory_days']+' days' for r in rows],
        [('Working inventory', [float(r['working_inventory_thousand_m3']) for r in rows])],
        show_legend=False, value_axis_format='0', axis_font_size=12, brand=brand)
    chart.value_axis.minimum_scale=0;chart.value_axis.maximum_scale=500;chart.value_axis.major_unit=100
    chart.plots[0].has_data_labels=True
    labels=chart.plots[0].data_labels;labels.position=XL_DATA_LABEL_POSITION.OUTSIDE_END
    labels.number_format='0';labels.font.name=cfg.THEME_FONT;labels.font.size=Pt(12);labels.font.color.rgb=brand.ink
    curve=chart.series[0];curve.format.fill.solid();curve.format.fill.fore_color.rgb=brand.accent_primary
    curve.format.line.fill.background()
    text(s, 'Working m³ = annual litres ÷ 365 ÷ 1,000 × inventory days', .5, 6.03, 7.05, .30, 12, True, brand.accent_primary)
    text(s, 'At 14 days: approximately 211 thousand m³ of working inventory.\nNew tanks depend on usable spare capacity, peaks, product segregation and dispatch limits.',
         .5, 6.48, 7.05, .55, 11.5)
    s.notes_slide.notes_text_frame.text += '\nIllustration contract: storage_inventory_sensitivity_2026_10_06.csv. Values = 5.5e9 litres/year / 365 days/year * authored days / 1000 litres/m3 / 1000 m3 per plotted unit. Uniform flows; no peak factor, heel, headroom, spare existing capacity, product segregation or capex assumptions. These are required working stocks, not gross nameplate or new capacity. Owner Nigel / Manish; expiry: reviewed customer flows and inventory policy. Presentation illustration only; not an operational model input.'
