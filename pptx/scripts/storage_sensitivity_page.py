"""Render a declared reporting illustration; no investment model is executed."""
from pptx.util import Inches, Pt
from pptx.enum.chart import XL_CHART_TYPE, XL_DATA_LABEL_POSITION
from brand_pptx import add_themed_chart
from brand_configs import vopak as cfg
from supply_review_pages import read, frame


def add_storage_sensitivity_page(s, text, root, brand):
    rows = read(root/'story/storage_inventory_sensitivity_2026_10_06.csv')
    case=rows[1]
    frame(s, f"Illustrative additional flows require {float(case['working_inventory_thousand_m3']):.0f} thousand m³ at {case['inventory_days']} inventory days",
          'Working inventory sensitivity | illustrative, thousand m³',
          'Existing 5.5 bn L/year candidate example; authored inventory-day sensitivity, 6 Oct 2026. Not new-capacity sizing.', text, brand)
    # One self-contained exhibit: unit, flow assumption, categories and direct values.
    for q in list(s.shapes):
        if Inches(1.7)<=q.top<Inches(7.05):q._element.getparent().remove(q._element)
    text(s,'Working inventory, thousand m³',.5,1.78,5.4,.35,14,True)
    text(s,'Illustrative: 5.5 bn litres/year; uniform daily flow',6.0,1.82,6.15,.30,11)
    chart = add_themed_chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED,
        Inches(.5), Inches(2.28), Inches(11.65), Inches(3.95),
        [r['inventory_days']+' days' for r in rows],
        [('Working inventory (thousand m³)', [float(r['working_inventory_thousand_m3']) for r in rows])],
        show_legend=False, value_axis_format='0', axis_font_size=14, brand=brand)
    chart.value_axis.minimum_scale=0;chart.value_axis.maximum_scale=500;chart.value_axis.major_unit=100
    chart.plots[0].gap_width=110
    chart.plots[0].has_data_labels=True
    labels=chart.plots[0].data_labels;labels.position=XL_DATA_LABEL_POSITION.OUTSIDE_END
    labels.number_format='0';labels.font.name=cfg.THEME_FONT;labels.font.size=Pt(18);labels.font.bold=True;labels.font.color.rgb=brand.ink
    curve=chart.series[0];curve.format.fill.solid();curve.format.fill.fore_color.rgb=brand.accent_primary
    curve.format.line.fill.background()
    point=curve.points[1];point.format.fill.solid();point.format.fill.fore_color.rgb=brand.accent_secondary
    text(s,'Inventory days',.5,6.35,11.65,.27,12,True)
    text(s,'Working stock, not new capacity: allow for spare tanks, peaks, product segregation, tank heels and dispatch limits.',
         .5,6.78,11.65,.29,11)
    s.notes_slide.notes_text_frame.text+='\nChart-first feedback: calculation and detailed operating checks retained in notes. Nigel confirms candidate flows and inventory policy; Manish and Henry test usable spare tanks, peaks and operating allowances. Working m³ = annual litres / days per year / litres per m³ * inventory days. Full-width native editable chart; direct data labels; highlighted 14-day illustrative case.'
    s.notes_slide.notes_text_frame.text += '\nIllustration contract: storage_inventory_sensitivity_2026_10_06.csv. Values = 5.5e9 litres/year / 365 days/year * authored days / 1000 litres/m3 / 1000 m3 per plotted unit. Uniform flows; no peak factor, heel, headroom, spare existing capacity, product segregation or capex assumptions. These are required working stocks, not gross nameplate or new capacity. Owner Nigel / Manish; expiry: reviewed customer flows and inventory policy. Presentation illustration only; not an operational model input.'
