"""Stage new review evidence in a draft vintage; register without adopting it."""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

import yaml

from lfm.config import Paths
from lfm.governance import inventory, read_rows
from lfm.sources.sa_review import parse_eskom_history, parse_worldbank


def write_rows(path, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, required=True)
    parser.add_argument('--eskom-text', type=Path, required=True)
    args = parser.parse_args()
    root = Paths.default().repo_root
    base = root / 'assumptions/2026'
    if yaml.safe_load((base / '_meta.yaml').read_text())['status'] != 'draft':
        raise ValueError('Only a draft vintage may receive new review evidence')
    declaration = base / 'sa_review.yaml'
    if declaration.exists():
        raise ValueError('Review evidence already staged; reconcile changes explicitly')
    text = args.eskom_text.read_text(encoding='utf-8')
    pages = re.split(r'(?m)^PDF PAGE \d+\n', text)[1:]
    eskom = parse_eskom_history(pages)
    investment = []
    for file, indicator in [('worldbank_fdi.json', 'BX.KLT.DINV.WD.GD.ZS'), ('worldbank_gfcf.json', 'NE.GDI.FTOT.ZS')]:
        investment += parse_worldbank(json.loads((args.raw_dir / file).read_bytes()), indicator)
    ts = base / 'timeseries'
    for filename in ('eskom_fuel_eaf_review_2026_10_07.csv', 'investment_review_2026_10_07.csv'):
        if (ts / filename).exists():
            raise ValueError(f'Preserve existing dataset: {filename}')
    write_rows(ts / 'eskom_fuel_eaf_review_2026_10_07.csv', eskom)
    write_rows(ts / 'investment_review_2026_10_07.csv', investment)
    common = dict(exception_id='EXC-SA-REVIEW-2026-10-07', owner='nigel.zhuwaki',
                  confidence='unassessed', last_updated='2026-10-07', shared=True,
                  provisional=True, needs_verification=True)
    blocks = {
        'eskom_history': dict(common, register_id='REG-SA-REVIEW-ESKOM', csv='timeseries/eskom_fuel_eaf_review_2026_10_07.csv',
                             units='per-row unit; FY ending 31 March', source='Eskom Integrated Report 2025; PDF page in each row; provenance in sa_review_evidence.sources.yaml'),
        'investment_history': dict(common, register_id='REG-SA-REVIEW-INVESTMENT', csv='timeseries/investment_review_2026_10_07.csv',
                                 units='percent of GDP; calendar year', source='World Bank WDI API BX.KLT.DINV.WD.GD.ZS and NE.GDI.FTOT.ZS; provenance in sa_review_evidence.sources.yaml'),
        'lesedi_catchment': dict(common, register_id='REG-SA-REVIEW-LESEDI', value='GP', units='South African province code',
                                source='User instruction 7 October 2026: use Gauteng for now. Provisional reporting boundary; not proof of commercial reach.'),
    }
    declaration.write_text(yaml.safe_dump(blocks, sort_keys=False), encoding='utf-8')
    source_pdf = root / 'external/data/refresh_20261005/raw/eskom/eskom-integrated-report-2025.pdf'
    manifest = json.loads((args.raw_dir / 'manifest.json').read_text())
    meta = dict(retrieved='2026-10-07', status='source extracted; independent verification and model adoption pending',
                eskom=dict(file=source_pdf.relative_to(root).as_posix(), sha256=hashlib.sha256(source_pdf.read_bytes()).hexdigest(),
                           url='https://www.eskom.co.za/investors/integrated-results/',
                           limitation='Fuel volume includes kerosene; Eskom-only. Cost includes storage/demurrage. FY2026 fuel volume not found in the local integrated report.'),
                investment=[m for m in manifest if m['id'].startswith('worldbank_')],
                exclusions=['No adoption elasticity inferred from prices', 'FDI may reflect ownership transactions, not new productive capacity'])
    (base / 'sa_review_evidence.sources.yaml').write_text(yaml.safe_dump(meta, sort_keys=False), encoding='utf-8')
    # Source metadata must live below the domain-YAML scan, not as an assumption domain.
    (base / 'sa_review_evidence.sources.yaml').rename(ts / 'sa_review_evidence.sources.yaml')
    register_path = root / 'governance/assumption_register.csv'
    register = read_rows(register_path)
    known = {r['assumption'] for r in register}
    added = 0
    with register_path.open('a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(register[0]))
        for item in inventory(Paths.default(), '2026'):
            if not item['block'].startswith('sa_review.') or item['assumption'] in known:
                continue
            row = {k: item.get(k, '') for k in register[0]}
            row.update(id='LOC-' + hashlib.sha256(item['assumption'].encode()).hexdigest()[:12], reviewer='', review_status='unreviewed')
            writer.writerow(row)
            added += 1
    ep = root / 'governance/exception_log.csv'
    exceptions = read_rows(ep)
    row = dict.fromkeys(exceptions[0], '')
    row.update(id='EXC-SA-REVIEW-2026-10-07', assumption='sa_review.*; model.scenario_levers',
               reason='New extracted review evidence and provisional Gauteng boundary; marginal scenario coefficients and commercial inputs remain uncalibrated.',
               owner='nigel.zhuwaki', risk='Mixed fiscal/calendar periods, fuel boundaries, uncalibrated diversion or unmatched market shares could distort conclusions.',
               expiry_trigger='Before forecast integration, market-share publication or investment recommendation', expires_on='2026-11-12',
               migration_path='Manish reconcile originals and operating/customer data; Nigel confirm boundaries and assumptions; Henry review mechanisms before adoption.',
               status='open', validity='2026')
    if any(x['id'] == row['id'] for x in exceptions):
        raise ValueError('Exception already exists; reconcile rather than duplicate')
    with ep.open('a', encoding='utf-8', newline='') as f:
        csv.DictWriter(f, fieldnames=list(exceptions[0])).writerow(row)
    print(f'Staged {len(eskom)} Eskom and {len(investment)} investment observations; added {added} unreviewed register rows.')


if __name__ == '__main__':
    main()
