"""Build the 10 October market review from registered evidence and assumptions."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import yaml
from lfm.config import Paths
from lfm.model.market_review import capture_screen, handling_bn_l, pipeline_context


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def build(vintage: Path) -> dict:
    config = yaml.safe_load((vintage / 'market_review.yaml').read_text('utf8'))
    screen = config['screen']['value']
    pipe = config['pipeline_evidence']['value']
    products = screen['products']
    ts = vintage / 'timeseries'
    trade = read(ts / 'fuel_trade_sars_by_office.csv')
    national = read(ts / 'fuel_sales_department.csv')
    provincial = read(ts / 'fuel_sales_department_by_province.csv')
    site_rows = read(vintage / 'infrastructure/terminal_site_assumptions.csv')
    trade_rows = [r for r in trade if int(r['period']) == screen['trade_year'] and r['product'] in products and r['unit'] == 'litres']
    def volumes(rows, predicate):
        vals = {p: sum(float(r['value']) for r in rows if r['product'] == p and predicate(r)) / 1e9 for p in products}
        return {**vals, 'total': sum(vals.values())}
    gross = volumes(trade_rows, lambda r: r['flow'] == 'import')
    exports = volumes(trade_rows, lambda r: r['flow'] == 'export')
    gateway = volumes(trade_rows, lambda r: r['flow'] == 'import' and r['district_office'] == 'Durban')
    national_sales = volumes(national, lambda r: int(r['period']) == screen['national_sales_year'])
    sales_rows = [r for r in provincial if int(r['period']) == screen['provincial_sales_year']]
    catchments = {name: volumes(sales_rows, lambda r, codes=codes: r['province'] in codes) for name, codes in
                  [('KZN', ['KZN']), ('Gauteng', ['GP']), ('Six inland provinces', screen['inland_provinces'])]}
    sites = {}
    for short in ('Durban', 'Lesedi'):
        rows = [r for r in site_rows if r['site'] == 'Vopak ' + short]
        capacity_rows = [r for r in rows if r['parameter'] == 'operational_capacity']
        working = sum(float(r['value']) for r in capacity_rows)
        cases = {case: float(next(r['value'] for r in rows if r['parameter'] == 'monthly_turns_' + case)) for case in ('low', 'base', 'high')}
        sites[short] = dict(working_m3=working, estimated_component_m3=sum(float(r['value']) for r in capacity_rows if r['basis'] == 'estimate'),
                            monthly_turns=cases, handling_bn_l={k: handling_bn_l(working, v) for k, v in cases.items()})
    scenarios = []
    for name, fraction in screen['capture_cases'].items():
        scenarios.append(dict(case=name, gateway_capture_fraction=fraction, lesedi_routing_fraction=screen['lesedi_fraction_of_captured_durban_flow'],
                              **capture_screen(gateway['total'], fraction, screen['lesedi_fraction_of_captured_durban_flow'],
                                sites['Durban']['handling_bn_l'][screen['operating_case']], sites['Lesedi']['handling_bn_l'][screen['operating_case']])))
    paths = [vintage / 'market_review.yaml', ts / 'fuel_trade_sars_by_office.csv', ts / 'fuel_sales_department.csv',
             ts / 'fuel_sales_department_by_province.csv', vintage / 'infrastructure/terminal_site_assumptions.csv']
    return dict(date='2026-10-10', status='provisional screening, not forecast or market-share evidence',
                years={k: screen[k] for k in ('trade_year', 'national_sales_year', 'provincial_sales_year')},
                national_sales=national_sales, gross_imports=gross, exports=exports,
                net_imports={k: gross[k]-exports[k] for k in gross}, durban_customs=gateway,
                durban_import_share_pct=gateway['total']/gross['total']*100, catchments=catchments, sites=sites,
                pipeline={**pipe, **pipeline_context(pipe['mpp_usage_million_litres_week'], pipe['mpp_capacity_million_litres_week'], pipe['annualisation_weeks'])},
                scenarios=scenarios, input_sha256={str(p.relative_to(vintage)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                limitations=['Gateway customs office is a port proxy, not measured terminal movements.',
                             'Capture fractions and the 50% onward routing assumption are authored sensitivities, not empirical bounds.',
                             'Existing base turns remain fixed in capture cases; route access and customer allocation are conditions, not validated constraints.',
                             'Lesedi other-terminal and domestic receipts are excluded. This is a single imported chain, not the full Vopak portfolio.',
                             'No existing throughput baseline is available, so these are total scenario volumes, not incremental volumes.',
                             'Working tankage is partly estimated. Tank arithmetic is not a guaranteed engineering ceiling.',
                             'Fiscal pipeline measures and calendar customs measures retain separate scopes. No road/rail flow residual is calculated.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vintage', default='2026')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    result = build(Paths.default().vintage_dir(args.vintage))
    (args.output / 'market_review.json').write_text(json.dumps(result, indent=2), encoding='utf8')
    with (args.output / 'capture_scenarios.csv').open('w', newline='', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=list(result['scenarios'][0])); writer.writeheader(); writer.writerows(result['scenarios'])
    print(json.dumps({k: result[k] for k in ('national_sales', 'gross_imports', 'durban_customs', 'scenarios')}, indent=2))


if __name__ == '__main__':
    main()
