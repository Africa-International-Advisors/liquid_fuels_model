"""Fail-closed parsers for the signed-off South Africa evidence review."""
from __future__ import annotations

import re


def parse_eskom_history(pages: list[str]) -> list[dict]:
    """FY2025 report: ten-year EAF/fuel-use tables and FY2023-25 own OCGT cost.

    Litres cover Eskom diesel AND kerosene, not independent producers or private
    backup. Cost includes storage/demurrage and is not gross cash diesel spend.
    Exact target/actual table layout is required; a changed report must be reviewed.
    """
    rows = []
    for number, page in enumerate(pages, 1):
        for line in page.splitlines():
            if 'Diesel and kerosene usage for OCGTs' in line:
                values = re.findall(r'\d{1,3}(?: \d{3})*\.\d+', line)
                if len(values) != 10 or '2025 2024 2023 2022 2021 2020 2019 2018 2017 2016' not in re.sub(r'\s+', ' ', page):
                    raise ValueError('Unexpected Eskom ten-year fuel table')
                rows += _rows(values, range(2025, 2015, -1), 'eskom_ocgt_diesel_and_kerosene', 'million litres', number)
            if line.startswith('Energy availability factor (EAF), %'):
                values = re.findall(r'\d{1,2}\.\d{2}', line)
                if len(values) == 10:
                    rows += _rows(values, range(2025, 2015, -1), 'eskom_eaf', 'percent', number)
            if line.startswith('OCGT diesel usage, R million'):
                # Six values: three targets followed by actual FY2025/24/23.
                values = re.findall(r'(?<!\d)\d{1,2} \d{3}(?!\d)', line)
                if len(values) != 6:
                    raise ValueError('Unexpected Eskom target/actual cost table')
                rows += _rows(values[-3:], (2025, 2024, 2023), 'eskom_ocgt_cost_including_storage_demurrage', 'million ZAR', number)
    keys = [(r['series'], r['period']) for r in rows]
    if len(rows) != 23 or len(set(keys)) != 23:
        raise ValueError(f'Expected 23 distinct Eskom observations, found {len(rows)}')
    return sorted(rows, key=lambda r: (r['series'], r['period']))


def _rows(values, years, series, unit, page):
    return [dict(country='ZAF', period=y, scenario='shared', series=series,
                 value=float(v.replace(' ', '')), unit=unit, pdf_page=page,
                 source_report=2025, period_basis='financial year ending 31 March')
            for y, v in zip(years, values)]


def parse_worldbank(payload: list, indicator: str) -> list[dict]:
    if not isinstance(payload, list) or len(payload) != 2 or payload[0].get('pages') != 1:
        raise ValueError('Expected one complete World Bank response page')
    rows = []
    for item in payload[1]:
        if item['countryiso3code'] != 'ZAF' or item['indicator']['id'] != indicator:
            raise ValueError('Unexpected country or indicator')
        if item['value'] is None:
            continue  # Missing is not zero; coverage is disclosed in the report.
        rows.append(dict(country='ZAF', period=int(item['date']), scenario='shared',
                         series=indicator, value=float(item['value']), unit='percent of GDP',
                         source_update=payload[0].get('lastupdated', ''), period_basis='calendar year'))
    if len({r['period'] for r in rows}) != len(rows):
        raise ValueError('Duplicate World Bank year')
    return sorted(rows, key=lambda r: r['period'])
