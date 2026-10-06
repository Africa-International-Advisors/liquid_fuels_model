from pathlib import Path
from pypdf import PdfReader
from lfm.scripts.collect_freight_review import totals

def test_preserved_freight_report_vintages_are_not_spliced():
    raw=Path(__file__).resolve().parents[1]/'external/data/raw/demand_drivers_20261006'
    older=totals(PdfReader(raw/'P7162December2024.pdf'))
    newer=totals(PdfReader(raw/'P7162December2025.pdf'))
    assert older[2024]['road']==790611
    assert newer[2024]['road']==979798
    assert newer[2025]=={'rail':168263,'road':976468}
