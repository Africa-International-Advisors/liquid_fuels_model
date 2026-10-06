"""Audit newly collected reporting evidence against preserved source reports."""
from pathlib import Path
from pypdf import PdfReader
from lfm.scripts.collect_supply_review import extract_trade, extract_capacity

RAW=Path(__file__).resolve().parents[1]/'external/data/raw/fuel_supply_review_20261006'

def test_trade_source_pages_and_product_scope():
    rows=extract_trade(PdfReader(RAW/'trade2024.pdf'))
    assert len(rows)==12
    assert next(r['value'] for r in rows if r['period']==2024 and r['product']=='diesel' and r['flow']=='import')==10.8e9
    assert {r['product'] for r in rows}=={'petrol','diesel','jet'}
    assert {r['pdf_page'] for r in rows}=={13,14}

def test_capacity_keeps_dashes_and_synthetic_basis_explicit():
    rows=extract_capacity(PdfReader(RAW/'annual-report-2025.pdf'))
    assert sum(r['value'] for r in rows if r['period']==2020)==718000
    assert sum(r['value'] for r in rows if r['period']==2025)==358000
    sapref=next(r for r in rows if r['period']==2025 and r['asset']=='Sapref')
    assert sapref['report_cell']=='dash; excluded from reported total'
    assert all(r['basis']=='crude equivalent' for r in rows if r['asset']=='Sasol')
