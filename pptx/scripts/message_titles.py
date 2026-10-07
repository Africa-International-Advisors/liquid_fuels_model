"""Apply evidence-led message titles to the approved 31-page review deck.

Preserves page order, native exhibits, notes and all analytical values.
"""
import json
import sys
from copy import deepcopy
from pathlib import Path

from pptx import Presentation


def main(source, destination):
    root = Path(__file__).resolve().parents[1]
    spec = json.loads((root / 'story/message_titles_2026_10_07.json').read_text(encoding='utf-8'))
    deck = Presentation(source)
    assert len(deck.slides) == 31
    changes = []
    for entry in spec['titles']:
        slide = deck.slides[entry['page'] - 1]
        shape = slide.shapes.title
        assert shape is not None
        previous = shape.text
        paragraph = shape.text_frame.paragraphs[0]
        style = deepcopy(paragraph.runs[0]._r.rPr) if paragraph.runs else None
        paragraph.clear()
        run = paragraph.add_run()
        run.text = entry['title']
        if style is not None:
            run._r.insert(0, style)
        for extra in list(shape.text_frame.paragraphs)[1:]:
            extra._p.getparent().remove(extra._p)
        changes.append(dict(entry, previous_title=previous))
    target = Path(destination)
    if target.exists():
        raise FileExistsError(f'Preserve existing output: {target}')
    deck.save(target)
    target.with_suffix('.titles.json').write_text(json.dumps(changes, indent=2), encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
