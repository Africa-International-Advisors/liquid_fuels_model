"""Build source-linked review exhibits and a work tracker, preserving prior packs."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from html import escape
import json
import math
from pathlib import Path
import shutil
import subprocess

import pandas as pd
import yaml

from lfm.assumptions import YamlDirectoryProvider
from lfm.assumptions.snapshot import SnapshotProvider
from lfm.config import Paths
from lfm.model.demand import vehicles
from lfm.reporting.sa_review import annual_series, complete_period_totals, endpoint_change, rebase
from lfm.run import Run


COLOURS = ('#0A2373', '#546CA2', '#767676', '#008477')


def line_svg(series, unit, *, forecast=False):
    """Editable SVG business chart; missing years break lines rather than interpolate."""
    values = [(y, v) for _, points in series for y, v in points.items()]
    if not values:
        raise ValueError('Cannot publish an exhibit without comparable observations')
    if any(not math.isfinite(v) for _, v in values):
        raise ValueError('Non-finite chart observation')
    xmin, xmax = min(y for y, _ in values), max(y for y, _ in values)
    ymin = min(0, min(v for _, v in values))
    ymax = max(v for _, v in values)
    span = max(ymax - ymin, 1)
    ymax += span * .12
    x = lambda y: 75 + (y - xmin) / max(xmax - xmin, 1) * 745
    y = lambda v: 260 - (v - ymin) / (ymax - ymin) * 210
    pieces = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 340" role="img" aria-label="'+escape(unit)+'"><rect width="880" height="340" fill="white"/>',
              '<g font-family="Lato,Arial,sans-serif" font-size="12" fill="#404040">',
              f'<text x="15" y="20">{escape(unit)}</text>']
    for j in range(5):
        value = ymin + (ymax - ymin) * j / 4
        yy = y(value)
        pieces += [f'<line x1="75" y1="{yy:.1f}" x2="820" y2="{yy:.1f}" stroke="#dedede"/>',
                   f'<text x="65" y="{yy+4:.1f}" text-anchor="end">{value:,.1f}</text>']
    step = max(1, math.ceil((xmax-xmin)/9))
    for year in sorted(set(range(xmin, xmax+1, step)) | {xmax}):
        pieces.append(f'<text x="{x(year):.1f}" y="280" text-anchor="middle">{year}</text>')
    for index, (label, points) in enumerate(series):
        colour = COLOURS[index % len(COLOURS)]
        prior = None
        for year, value in sorted(points.items()):
            if prior is not None and year == prior[0] + 1:
                dash = ' stroke-dasharray="5 4"' if forecast else ''
                pieces.append(f'<line x1="{x(prior[0]):.1f}" y1="{y(prior[1]):.1f}" x2="{x(year):.1f}" y2="{y(value):.1f}" stroke="{colour}" stroke-width="2.5"{dash}/>')
            pieces.append(f'<circle cx="{x(year):.1f}" cy="{y(value):.1f}" r="3" fill="{colour}"><title>{escape(label)} {year}: {value:,.3f}</title></circle>')
            prior = (year, value)
        lx = 75 + (index % 2) * 390
        ly = 308 + (index // 2) * 21
        pieces += [f'<line x1="{lx}" y1="{ly-4}" x2="{lx+18}" y2="{ly-4}" stroke="{colour}" stroke-width="3"/>',
                   f'<text x="{lx+26}" y="{ly}">{escape(label)}</text>']
    return ''.join(pieces) + '</g></svg>'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    root = Paths.default().repo_root
    out = args.output_dir.resolve()
    if not out.is_relative_to(root / 'output'):
        raise ValueError('Report output must stay under output/')
    out.mkdir(parents=True, exist_ok=False)
    hashes = {}
    def read(path):
        file = root / path
        hashes[path] = hashlib.sha256(file.read_bytes()).hexdigest()
        return pd.read_csv(file)
    ts = 'assumptions/2026/timeseries/'
    charts = []
    chart_rows = []
    def chart(key, title, data, unit, note, source, forecast=False):
        svg = line_svg(data, unit, forecast=forecast)
        (out / f'{key}.svg').write_text(svg, encoding='utf-8')
        charts.append(dict(id=key, title=title, svg=svg, note=note, source=source))
        for label, points in data:
            chart_rows.extend(dict(exhibit=key, series=label, period=year, value=value, unit=unit, source=source,
                                   status='current draft engine; not calibrated' if forecast else 'staged reported observation; not independently verified')
                              for year, value in sorted(points.items()))
    dept = read(ts+'fuel_sales_department.csv')
    fiasa = read(ts+'fuel_sales_fiasa.csv')
    sales = {p: annual_series(dept[(dept['product']==p) & (dept.quarters_reported==4) & (dept.period>=2013)], scale=1e9) for p in ('petrol','diesel')}
    separate = {p: annual_series(fiasa[(fiasa['product']==p) & (fiasa.period==2024)], scale=1e9) for p in ('petrol','diesel')}
    chart('01_demand', 'Petrol and diesel have different historical trajectories',
          [('Petrol: department', sales['petrol']), ('Diesel: department', sales['diesel']),
           ('Petrol: FIASA 2024', separate['petrol']), ('Diesel: FIASA 2024', separate['diesel'])], 'billion litres / calendar year',
          'Department full-year sales through 2023. FIASA 2024 is shown separately, with unresolved revisions. These are reported sales, not an independently verified consumption balance.',
          ts+'fuel_sales_department.csv; '+ts+'fuel_sales_fiasa.csv')
    macro = read(ts+'macro_statssa.csv')
    gdp = annual_series(macro[(macro.series=='gdp') & (macro.basis=='actual') & macro.period.between(2013,2023)])
    chart('02_growth', 'GDP and fuel sales need separate explanations',
          [('Real GDP', rebase(gdp,2013)), ('Petrol sales', rebase(sales['petrol'],2013)), ('Diesel sales', rebase(sales['diesel'],2013))],
          'index: 2013 = 100; matched 2013-2023 window',
          'Co-movement does not establish causation or a demand elasticity. Investment and confidence should not be additional multipliers on an overlapping GDP effect.',
          ts+'macro_statssa.csv; '+ts+'fuel_sales_department.csv')
    investment = read(ts+'investment_review_2026_10_07.csv')
    chart('03_investment', 'Investment intensity and FDI provide economic context',
          [('Fixed capital formation', annual_series(investment[investment.series=='NE.GDI.FTOT.ZS'])),
           ('FDI net inflows', annual_series(investment[investment.series=='BX.KLT.DINV.WD.GD.ZS']))], 'percent of GDP / calendar year',
          'FDI can include large ownership transactions; it is not a measure of greenfield capex or investor confidence. Missing API observations are excluded, never replaced with zero.',
          'World Bank WDI: NE.GDI.FTOT.ZS and BX.KLT.DINV.WD.GD.ZS; '+ts+'investment_review_2026_10_07.csv')
    price_path = 'pptx/story/evidence_2026_10_06/fuel_prices_department_annual.csv'
    prices = read(price_path)
    chart('04_prices', 'Fuel-price volatility changes the economics of vehicle use',
          [('Petrol 95 inland retail', annual_series(prices[prices.series=='petrol_95_inland_retail'],scale=100)),
           ('Diesel 0.05% inland wholesale', annual_series(prices[prices.series=='diesel_005_inland_wholesale'],scale=100))], 'nominal ZAR/litre; full-year monthly averages',
          'Uses the existing 6 October reporting extract through 2025; the registered historical file currently stops in 2023. Petrol is retail; diesel is wholesale, not a pump-price comparison. EV economics require matched vehicle prices, consumption, tariffs and charging losses; adoption is not inferred.',
          price_path)
    power = read(ts+'eskom_fuel_eaf_review_2026_10_07.csv')
    power_series = {}
    for key, title, metric, unit, note in [
        ('05_eskom_fuel','Eskom OCGT fuel use fell sharply in FY2025','eskom_ocgt_diesel_and_kerosene','million litres / FY ending 31 March','Reported diesel AND kerosene for Eskom OCGTs; excludes IPP/private fuel use. FY2026 fuel-volume evidence remains open.'),
        ('06_eskom_eaf','EAF provides context for changing diesel generation','eskom_eaf','percent / FY ending 31 March','FY2016-2025 from one ten-year report table. EAF is not a direct diesel-dispatch equation; demand, outages and other supply also matter.'),
        ('07_eskom_cost','Eskom OCGT costs must retain their accounting boundary','eskom_ocgt_cost_including_storage_demurrage','million ZAR / FY ending 31 March','Eskom-only OCGT costs include storage and demurrage. Do not mix with gross diesel cash spend or combined Eskom/IPP cost releases.')]:
        points = annual_series(power[power.series==metric])
        power_series[metric] = points
        chart(key,title,[(metric.replace('eskom_','').replace('_',' '),points)],unit,note,ts+'eskom_fuel_eaf_review_2026_10_07.csv; Eskom Integrated Report 2025, row-level PDF pages')
    activity = read('pptx/story/evidence_2026_10_06/activity_statssa_monthly.csv')
    freight = []
    for mode in ('road','rail'):
        totals = complete_period_totals(activity[activity.series=='freight_payload_'+mode], periods_per_year=12)
        freight.append((mode.title(),{y:v/1000 for y,v in totals.items() if y>=2013}))
    chart('08_freight','Rail ambitions must be translated into transferable road freight',freight,'million tonnes / complete calendar year',
          'Stats SA national payloads are tonnes, not tonne-kilometres or corridor transfers. Latest revised annual report observations are retained separately. The 250 Mt network ambition cannot be subtracted directly from road freight.',
          'pptx/story/evidence_2026_10_06/activity_statssa_monthly.csv')
    revised = read(ts+'freight_payload_statssa_review.csv')
    revised.to_csv(out/'freight_revision_comparison_source.csv',index=False)
    quarterly = read(ts+'fuel_sales_department_by_province_quarterly.csv')
    scope = yaml.safe_load((root/'assumptions/2026/sa_review.yaml').read_text())
    catchment = scope['lesedi_catchment']['value']
    gauteng = {}
    for p in ('petrol','diesel'):
        totals = complete_period_totals(quarterly[(quarterly.province==catchment) & (quarterly['product']==p)], periods_per_year=4)
        gauteng[p] = {y:v/1e9 for y,v in totals.items()}
    chart('09_gauteng','Gauteng is the provisional Lesedi reporting catchment',[(p.title(),s) for p,s in gauteng.items()],
          'billion litres / complete calendar year',
          'User-selected boundary. Four distinct quarters required. The latest 2023-Q1 observation is not annualised. Provincial sales do not establish terminal reach, customer access or Vopak throughput.',
          ts+'fuel_sales_department_by_province_quarterly.csv; user scope decision 7 October 2026')
    trade = read('pptx/story/evidence_2026_10_06/fuel_trade_sars.csv')
    trade_data = []
    for p in ('petrol','diesel'):
        for flow in ('import','export'):
            sub = trade[(trade['product']==p) & (trade.flow==flow) & (trade.unit=='litres') & (trade.months_reported==12)]
            trade_data.append((p.title()+' '+flow,annual_series(sub,scale=1e9)))
    chart('10_trade','Import and export flows require consistent product and unit coverage',trade_data,'billion litres / complete calendar year',
          'Only rows explicitly reported in litres with twelve months. Kilograms, unspecified units and diesel-biodiesel blends excluded; no assumed density conversion. Trade is not terminal throughput.',
          'pptx/story/evidence_2026_10_06/fuel_trade_sars.csv')
    operations = read('pptx/story/evidence_2026_10_06/refinery_output_operators.csv')
    chart('11_plant_output','Secunda and Natref series need product and ownership boundaries',
          [(plant,annual_series(operations[operations.plant==plant])) for plant in ('Secunda','Natref')], 'million barrels / FY ending 30 June',
          'Secunda: all refined products, not petrol/diesel alone. Natref: Sasol-reported production, not always whole-refinery output; FY2026 includes production beyond Sasol share. Do not add these as a complete national supply series.',
          'pptx/story/evidence_2026_10_06/refinery_output_operators.csv')
    paths = Paths.default()
    diagnostic_series = []
    for scenario in ('high_demand','low_demand'):
        run = Run(vintage='2026', scenario=scenario)
        provider = SnapshotProvider(YamlDirectoryProvider(paths),run)
        diagnostics = []
        vehicles.compute_country_annual(provider,run,'ZAF',start_year=2024,diagnostics=diagnostics)
        diag = pd.DataFrame(diagnostics)
        diag = diag[(diag['product']=='petrol_95') & diag.year.between(2024,2035)]
        grouped = diag.groupby('year')[['litres','vehicle_km']].sum()
        diagnostic_series.append((scenario.replace('_',' '),{int(y):float(r.litres/r.vehicle_km*100) for y,r in grouped.iterrows() if r.vehicle_km>0}))
    chart('12_efficiency','Fleet efficiency already emerges from the cohort engine',diagnostic_series,'L/100km: modelled petrol ICE fleet, 2024-2035',
          'Current draft engine diagnostic, not observed data or approved scenario ranges. Cohort fuel use is fixed at entry; replacement changes the fleet average. OEM calibration and segment-specific EV adoption remain open.',
          'src/lfm/model/demand/vehicles.py; assumptions/2026/vehicles.yaml and declared efficiency CSVs',forecast=True)
    summary = dict(as_of='2026-10-07',lesedi_catchment=catchment,
                   demand_change_2013_2023_pct={p:endpoint_change(s,2013,2023) for p,s in sales.items()},
                   eskom_fuel_change_FY2024_FY2025_pct=endpoint_change(power_series['eskom_ocgt_diesel_and_kerosene'],2024,2025),
                   gauteng_latest_complete_year={p:max(s) for p,s in gauteng.items()},
                   output_status='review evidence and current-engine diagnostics; no calibrated new forecast or Vopak share')
    tracker_path = root/'workstreams/WS0_governance/workplan/sa_review_audit_2026_10_07.csv'
    shutil.copy2(tracker_path,out/'audit_tracker.csv')
    tracker = pd.read_csv(tracker_path).fillna('')
    findings_path = root/'workstreams/WS1_data_validation/sa_supply_findings_2026_10_07.json'
    findings = json.loads(findings_path.read_text())
    shutil.copy2(findings_path,out/'supply_findings.json')
    pd.DataFrame(chart_rows).to_csv(out/'exhibit_data.csv',index=False)
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    for path in sorted((root/'assumptions/2026').rglob('*')):
        if path.suffix in ('.yaml','.csv'):
            hashes[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    provenance = dict(created_at=datetime.now(timezone.utc).isoformat(),
                      code_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                      working_tree=subprocess.check_output(['git','status','--short'],text=True), source_hashes=hashes)
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    html = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>South Africa evidence implementation</title><style>body{font:16px Lato,Arial,sans-serif;color:#202020;margin:0}header{background:#0A2373;color:white;padding:36px max(5vw,24px)}main{max-width:1100px;margin:auto;padding:28px}h1{font-size:32px}h2{font-size:23px;color:#0A2373}h3{font-size:18px}section{margin:36px 0 56px;break-inside:avoid}p{line-height:1.55}svg{width:100%;height:auto}table{border-collapse:collapse;width:100%;font-size:13px}td,th{text-align:left;padding:10px;border-bottom:1px solid #ddd;vertical-align:top}small{display:block;color:#555;overflow-wrap:anywhere}a{color:#0A2373}nav a{margin-right:18px}header a{color:white}.note{border-left:4px solid #546CA2;padding:12px 18px;background:#f5f6f8}@media print{header{background:white;color:#0A2373}nav{display:none}section{page-break-inside:avoid}body{font-size:12px}}</style><header><h1>South Africa market story: implementation evidence</h1><p>7 October 2026 | Signed-off scope in progress | Gauteng provisional Lesedi catchment</p><nav><a href="#findings">Findings</a><a href="#exhibits">Exhibits</a><a href="#audit">Audit and next work</a></nav></header><main>']
    html.append('<section id="findings"><h2>What the first implementation establishes</h2><p class="note">This pack contains staged historical evidence, source-linked supply findings and existing-engine diagnostics. It does not present a calibrated new forecast, actual Vopak market share or an investment recommendation.</p>')
    changes = summary['demand_change_2013_2023_pct']
    html.append(f'<p>On the matched departmental series, 2013-2023 petrol sales changed by <b>{changes["petrol"]:+.1f}%</b> and diesel by <b>{changes["diesel"]:+.1f}%</b>. The historical story therefore needs separate fuel trajectories.</p>')
    html.append(f'<p>Eskom reported OCGT diesel-and-kerosene use changed by <b>{summary["eskom_fuel_change_FY2024_FY2025_pct"]:+.1f}%</b> from FY2024 to FY2025. This is Eskom-only fuel use; it does not measure all private backup generation.</p>')
    html.append('<p>Both existing scenarios ran in the initial source audit. Only 29 of the original 72 declared blocks were requested by the engine; registered presentation snapshots are not automatically active forecast levers. A malformed vehicle-source metadata file was repaired without altering its evidence.</p>')
    for item in findings['findings']:
        html.append(f'<h3>{escape(item["asset"])}</h3><p><b>Source finding:</b> {escape(item["fact"])} <a href="{escape(item["url"])}">Primary source</a></p><p><b>Interpretation:</b> {escape(item["interpretation"])}<br><b>Remaining work:</b> {escape(item["gap"])}</p>')
    html.append('</section><section id="exhibits"><h2>Historical exhibits and model diagnostic</h2><p><a href="exhibit_data.csv">Underlying exhibit data</a> | <a href="provenance.json">Source hashes and run provenance</a></p></section>')
    for c in charts:
        html.append(f'<section><h2>{escape(c["title"])}</h2>{c["svg"]}<p>{escape(c["note"])}</p><small>Source: {escape(c["source"])}</small><p><a href="{c["id"]}.svg">Open standalone SVG</a></p></section>')
    html.append('<section id="audit"><h2>Audit and next work</h2><p><a href="audit_tracker.csv">Download complete audit tracker</a></p><table><thead><tr><th>Topic / status</th><th>Next work / model state</th><th>Owner / resolution trigger</th></tr></thead><tbody>')
    for row in tracker.itertuples():
        html.append(f'<tr><td><b>{escape(row.id)} {escape(row.topic)}</b><br>{escape(row.status)}</td><td>{escape(row.action)}<br><small>{escape(row.model_state)}</small></td><td>{escape(row.owner)}<br>{escape(row.expiry_trigger)}</td></tr>')
    html.append('</tbody></table><p>Commercial share remains open: matched Vopak unique deliveries, Durban market definition, route access and working terminal capacity are required. Investment also needs tariffs, contracts, capex and a return hurdle. Four road corridors remain to be confirmed.</p></section></main></html>')
    (out/'index.html').write_text(''.join(html),encoding='utf-8')
    print(json.dumps(summary,indent=2))
    print(out/'index.html')


if __name__ == '__main__':
    main()
