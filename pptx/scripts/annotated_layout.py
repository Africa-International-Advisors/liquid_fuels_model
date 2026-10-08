"""Apply Nigel's seven annotated layout references to the latest analytical deck."""
import json
import sys
from copy import deepcopy
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from convergence_feedback import text, replace
from supply_review_pages import line
from analytical_revision import BRAND, BLUE, INK, drop


def size(shape, points):
    for p in shape.text_frame.paragraphs:
        p.font.size = Pt(points)
        for r in p.runs: r.font.size = Pt(points)


def main(source, destination):
    prs = Presentation(source)
    assert len(prs.slides) == 30
    s = prs.slides[3]
    charts = [q for q in s.shapes if q.has_chart]
    legends = []
    for q in list(s.shapes):
        if Inches(1.7) <= q.top < Inches(7.04) and not q.has_chart:
            if Inches(3.0) <= q.top < Inches(3.3):
                q.top -= Inches(.65); legends.append(q)
            else: drop(q)
    evidence = Path(source).with_suffix('.revision.json')
    data = json.loads(evidence.read_text())['national']
    for i, (product, ch) in enumerate(zip(['petrol', 'diesel'], charts)):
        x = .5 + i * 5.95
        text(s, product.capitalize() + ' | bn litres', x, 1.78, 5.5, .35, 15, True, INK)
        line(s, (x, 2.15), (x + 5.5, 2.15), INK, .7)
        ch.top = Inches(2.78); ch.height = Inches(2.95)
        line(s, (x, 5.96), (x + 5.5, 5.96), INK, .6)
        text(s, 'Insights', x, 6.07, 5.5, .27, 13, True, BLUE)
        d = data[product]
        insight = (f"2025 imports of {d['imports'][-1]:.2f} bn L less exports of {d['exports'][-1]:.2f} bn L "
                   f"left net imports of {d['net_imports'][-1]:.2f} bn L, up {d['net_import_change_pct']:.0f}% year on year.")
        text(s, insight, x, 6.43, 5.5, .51, 11, color=INK)

    s = prs.slides[4]
    ch = next(q for q in s.shapes if q.has_chart)
    ch.width = Inches(4.95)
    codes = ['GP', 'KZN', 'WC', 'MP', 'EC', 'FS', 'NW', 'LP', 'NC']
    labels = [q for q in s.shapes if q.has_text_frame and q.text in codes and q.top > Inches(6)]
    swatches = [q for q in s.shapes if q.shape_type == 9 and q.left >= Inches(6) and q.top > Inches(6)]
    assert len(labels) == len(swatches) == 9
    for i, (label, swatch) in enumerate(zip(labels, swatches)):
        y = 3.05 + i * .34
        label.left = Inches(11.53); label.top = Inches(y); label.width = Inches(.58)
        swatch.left = Inches(11.20); swatch.top = Inches(y + .09); swatch.width = Inches(.22)
    # Extend the map panel down, keeping the actual geography at its latest uniform scale.
    for q in s.shapes:
        if q.name.startswith('Map frame'):
            q.height += Inches(.38)
        elif q.left < Inches(6.02) and Inches(3.3) <= q.top < Inches(6.3):
            q.top += Inches(.18)

    # Use the existing template-style divider marker rather than a new symbol.
    template = prs.slides[8]
    markers = [q for q in template.shapes if q.name.startswith('SCR divider marker:')]
    for n, split, right in [(7, 8.62, 8.8), (8, 7.88, 8.12)]:
        s = prs.slides[n - 1]
        line(s, (split, 2.13), (split, 6.9), INK, .6)
        line(s, (right, 2.13), (12.15, 2.13), INK, .6)
        if n == 7:
            line(s, (.5, 2.13), (8.4, 2.13), INK, .6)
            text(s, 'Insights', right, 1.78, 3.35, .34, 14, True, INK)
            heading = next(q for q in s.shapes if q.has_text_frame and q.text.startswith('Capacity by refinery'))
            heading.width = Inches(8)
        for q in markers:
            element = deepcopy(q._element)
            s.shapes._spTree.insert_element_before(element, 'p:extLst')
            added = s.shapes[-1]
            added.left += Inches(split - 7.88)
            # Ensure copied shape ids remain unique in the destination slide.
            for node in element.xpath('.//p:cNvPr'):
                node.set('id', str(max(sh.shape_id for sh in s.shapes) + 1))

    s = prs.slides[8]
    for q in s.shapes:
        if q.has_text_frame and q.text in ['Implication for Vopak', 'Existing gateways and potential inland distribution nodes']:
            size(q, 14)
    # Restore the right rule if the previous panel rebuild removed it.
    if not any(abs(q.top - Inches(2.13)) < 10 and q.left >= Inches(8) and q.height == 0 for q in s.shapes):
        line(s, (8.12, 2.13), (12.15, 2.13), INK, .6)

    for n in [10, 11]:
        s = prs.slides[n - 1]
        heading = next(q for q in s.shapes if q.has_text_frame and q.left == Inches(.5) and abs(q.top - Inches(1.78)) < 10)
        heading.top = Inches(1.65)
        size(heading, 13)
        for q in s.shapes:
            if q.name in ['Footprint legend', 'Demand legend', 'Handling legend']:
                q.top = Inches(2.09)
            elif q.has_text_frame and q.text in ['Vopak', 'Other listed', 'Reported demand'] and q.left < Inches(7.7):
                q.top = Inches(2.03)
            elif q.shape_type == 9 and q.left == Inches(.5) and abs(q.top - Inches(2.13)) < 10:
                q.top = Inches(2.35)
        if n == 10:
            for q in s.shapes:
                if q.has_text_frame and q.text in ['Region / provinces', 'Storage location', 'Published tank capacity']:
                    q.top = Inches(2.55)
    out = Path(destination)
    if out.exists(): raise FileExistsError(out)
    prs.save(out)
    print(out)


if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
