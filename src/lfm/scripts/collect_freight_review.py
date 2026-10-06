"""Preserve freight report vintages; never splice materially revised road series."""
import csv, hashlib, json, re
from pathlib import Path
from pypdf import PdfReader

def totals(reader):
    page=reader.pages[6].extract_text(extraction_mode='layout').split('Table 2')[0]
    assert 'Table 1' in page and 'Payload' in page and '000 tons' in page
    year=None; result={}
    for line in page.splitlines():
        line=line.strip()
        match=re.match(r'(202\d)\s+Jan ',line)
        if match: year=int(match[1])
        if line.startswith('Total '):
            tokens=re.split(r'\s{2,}',line)[1:]
            values=[int(t.replace(' ','')) for t in tokens]
            assert len(values)==6,(line,values)
            assert abs(values[0]+values[2]-values[4])<=2
            result[year]={'rail':values[0],'road':values[2]}
    assert len(result)==2
    return result

def main():
    root=Path(__file__).resolve().parents[3]
    raw=root/'external/data/raw/demand_drivers_20261006'
    reports={year:totals(PdfReader(raw/f'P7162December{year}.pdf')) for year in (2024,2025)}
    rows=[]
    for year,modes in reports[2025].items():
        for mode,value in modes.items():
            rows.append(dict(country='ZAF',period=year,scenario='shared',mode=mode,value=value,
                unit='thousand tonnes',basis='unadjusted all freight; report vintage December 2025',source_file='P7162December2025.pdf',pdf_page=7))
    out=root/'assumptions/2026/timeseries/freight_payload_statssa_review.csv'
    with out.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    meta={'retrieved':'2026-10-06','status':'staged reporting; no diesel displacement inferred',
        'refresh':'Download next P7162 December report; rerun extractor and compare overlapping years before adoption.',
        'sources':[{'file':f'P7162December{year}.pdf','url':f'https://www.statssa.gov.za/publications/P7162/P7162December{year}.pdf',
                    'sha256':hashlib.sha256((raw/f'P7162December{year}.pdf').read_bytes()).hexdigest()} for year in reports],
        'overlap_2024':[{'mode':mode,'old_value':reports[2024][2024][mode],
                        'new_value':reports[2025][2024][mode],
                        'delta':reports[2025][2024][mode]-reports[2024][2024][mode],
                        'status':'source revision; do not splice vintages'} for mode in ('rail','road')]}
    (out.with_suffix('.sources.json')).write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print(meta['overlap_2024'])

if __name__=='__main__':main()
