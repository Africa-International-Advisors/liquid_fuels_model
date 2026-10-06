"""Sourced regional demand and public storage competitors; share gaps remain explicit."""
import csv
import hashlib
from pptx.util import Pt, Inches
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from provincial_demand_map import sales
from storage_footprint import storage_notes
from exhibit_typography import CHART_LABEL, CHART_SECONDARY


def add_competitive_page(slide, exhibit_layout, Map, text, table, root, brand, regional):
    with (root/'story/competitive_market_evidence_2026_10_06.csv').open(encoding='utf-8-sig', newline='') as f:
        evidence = list(csv.DictReader(f))
    values, source, workbooks = sales(root)
    with (root/'story/demand_map_regions_2026_10_06.csv').open(encoding='utf-8-sig', newline='') as f:
        membership = list(csv.DictReader(f))
    region_names = ['Eastern coastal', 'Inland', 'Western coastal', 'Other / Northern Cape']
    totals = {name: sum(values[r['province_code']] for r in membership if r['region'] == name)
              for name in region_names}
    assert len(membership) == 9 and len({r['province_code'] for r in membership}) == 9
    assert abs(sum(totals.values()) - sum(values.values())) < 1e-9
    notes = ('Regional demand uses reported 2022 petrol/diesel sales, aggregated from all four quarters '
             'for nine provinces. Historical sales are a demand proxy, not current terminal catchments. '
             'No actual Vopak deliveries or contestable customer volumes were supplied for any region. '
             'No share percentage is calculated or imputed; unknown is not zero. '
             'The earlier illustrative 22.2/20.0% shares have been removed from this page. '
             'Other operators are potential competing or complementary storage providers, not confirmed '
             'direct competitors for every customer. Footprint is a starting inventory, not exhaustive. '
             'Storage capacities are stocks, not deliveries, and may include ineligible products. '
             'Obtain matched-year unique Vopak deliveries, customer destinations, transfer reconciliation, '
             'route costs, product-compatible capacity and contracts before calculating shares. '
             'Owner Manish; Nigel review. Refresh the source when a later complete provincial year is available. '
             f'Sales file: {source}; SHA256 {hashlib.sha256(source.read_bytes()).hexdigest()}; '
             f'received workbooks: {sorted(workbooks)}. Regional totals (bn litres): {totals}.\n'
             + storage_notes(root) + '\n'
             + '\n'.join(f"[{r['source_id']}] {r['operator']}: {r['source_url']} | {r['source_date']} | {r['limitation']}"
                         for r in evidence))
    s = slide('Size each regional market and locate competing storage',
              'DMPR 2022 provincial petrol/diesel sales; public operator sources [1-7], checked 6 Oct 2026. Share not established.',
              notes)
    exhibit_layout(s, 'All four regions | reported 2022 demand, bn litres/year', [])
    # Use the approved exhibit/divider layout; regional competitor detail replaces generic takeaways.
    for q in s.shapes:
        if q.has_text_frame and q.text == 'Key takeaways':
            q.text_frame.paragraphs[0].runs[0].text = 'Key takeaways | competitors'
    text(s, f'National total {sum(totals.values()):.2f} bn L | petrol + diesel; jet excluded',
         .5, 2.38, 7.05, .27, 11, True, brand.accent_primary)
    text(s, 'Region / provinces', .5, 2.87, 1.42, .56, CHART_LABEL, True)
    text(s, 'Reported demand', 2.02, 2.87, 2.78, .29, CHART_LABEL, True)
    text(s, 'Vopak\nserved', 4.98, 2.87, 1.15, .56, CHART_LABEL, True)
    text(s, 'Additional\ncontestable', 6.30, 2.87, 1.25, .56, CHART_LABEL, True)
    bar_x = 2.02; bar_width = 2.42; maximum = 12
    for v in [0, 4, 8, 12]:
        x = bar_x + bar_width*v/maximum
        text(s, str(v), x-.10, 3.32, .40, .24, CHART_SECONDARY)
        q = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(3.61), Inches(x), Inches(5.93))
        q.line.color.rgb = brand.grey_fill; q.line.width = Pt(.5)
    labels = [('Eastern coast', 'EC / KZN'), ('Inland', 'GP / FS / LP / MP / NW'),
              ('Western coast', 'WC'), ('Other', 'Northern Cape')]
    for i, (name, label) in enumerate(labels):
        y = 3.69 + i*.59; value = totals[region_names[i]]
        text(s, name, .5, y, 1.47, .29, CHART_LABEL, True)
        text(s, label.replace(" / ","/"), .5, y+.29, 1.47, .26, CHART_SECONDARY)
        width = bar_width*value/maximum
        q = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(bar_x), Inches(y+.08), Inches(width), Inches(.27))
        q.name = f'Reported 2022 petrol/diesel demand: {region_names[i]}: {value:.9f} bn L'
        q.fill.solid(); q.fill.fore_color.rgb = brand.accent_primary; q.line.fill.background()
        text(s, f'{value:.2f}', bar_x+width+.07, y+.08, .61, .29, CHART_LABEL, True)
        for x in [4.98, 6.30]:
            q = text(s, 'Not\nestablished', x, y+.02, 1.20, .49, CHART_LABEL)
            q.name = f'Unknown share input: {region_names[i]} at {x}'
    text(s, 'To calculate share: unique Vopak customer deliveries / same-year regional demand.',
         .5, 6.17, 7.05, .29, 10.5, True, brand.accent_primary)
    text(s, 'Contestable demand needs route cost, compatible tanks, contracts and switching evidence.\nCount Durban-Lesedi transfers once. Region boundaries are working groupings, not catchments.',
         .5, 6.51, 7.05, .44, 10)
    cards = [
        (2.40, '01 Eastern coast',
         'Vopak: Durban [1]. Bidvest: Durban and Richards Bay [2]; mixed-product capacity.\nTransnet: Ladysmith lease tanks [7].', .77),
        (3.55, '02 Inland',
         'Vopak: Lesedi [1]. Bidvest: Isando [2].\nSasol: Alrode, Pretoria West, Waltloo, Sasolburg [6]. Transnet: Tarlton / Jameson Park + four lease sites [7].', .91),
        (4.93, '03 Western coast',
         'Burgan Cape: Cape Town petrol/diesel terminal [3]. Confirm current tank availability and customer access.', .73),
        (6.00, '04 Other / Northern Cape',
         'Operator coverage incomplete. Check Shell site notices [4] and NERSA licences/access records [5].', .63),
    ]
    for y, heading, body, height in cards:
        text(s, heading, 8.12, y, 4.03, .31, 14, True, brand.accent_primary)
        text(s, body, 8.12, y+.36, 4.03, height, 12.5)
    # Every source number remains directly clickable in PPT and exported PDF.
    for i, r in enumerate(evidence):
        label = f"[{r['source_id']}] " + ['Vopak', 'Bidvest', 'Burgan', 'Shell', 'NERSA', 'Sasol', 'Transnet'][i]
        q = text(s, label, .5+i*.98, 6.99, .97, .17, 7.5, color=brand.accent_primary)
        for p in q.text_frame.paragraphs:
            for run in p.runs: run.hyperlink.address = r['source_url']
    return s
