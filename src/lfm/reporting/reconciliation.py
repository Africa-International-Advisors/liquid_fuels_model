"""Auditable 2024 accounting bridges to the inherited workbook.

These explain totals, not causal effects of independently estimated inputs.
The petrol midpoint bridge splits N*I exactly between stock and implied intensity.
Excel's intensity is demand divided by stock; it is not an independent km/efficiency
assumption. Diesel's non-power benchmark includes non-road uses, so its road residual
must be interpreted together with the explicit industrial/agriculture additions.
"""
from __future__ import annotations

import json
from pathlib import Path

import openpyxl
import pandas as pd

from lfm.assumptions import YamlDirectoryProvider
from lfm.model.demand import vehicles, aviation, generation, industrial, agriculture
from lfm.run import Run


def midpoint_bridge(n0, i0, n1, i1):
    return {'Fleet count / coverage': (n1-n0)*(i0+i1)/2,
            'Litres per vehicle / mix': (i1-i0)*(n0+n1)/2}


def build_reconciliation(workbook: Path, output: Path):
    wb = openpyxl.load_workbook(workbook, data_only=True, read_only=True)
    p = YamlDirectoryProvider()
    run = Run(vintage='2026', scenario='high_demand')
    detail = []
    road = vehicles.compute_country_annual(p, run, 'ZAF', diagnostics=detail).loc[2024]
    detail = pd.DataFrame(detail)
    observed = {
        'petrol': float(wb['Gasoline - DemandSupply']['K29'].value),
        'diesel': float(wb['Diesel - DemandSupply']['K30'].value),
        'jet': float(wb['Jet - DemandSupply']['J23'].value),
    }
    fleet0 = float(wb['Gasoline - DemandSupply']['T29'].value)
    fleet1 = float(detail[(detail.year == 2024) & (detail['product'] == 'petrol_95')]['stock'].sum())
    intensity0 = observed['petrol']/fleet0
    intensity1 = float(road.petrol_95)/fleet1
    petrol = midpoint_bridge(fleet0, intensity0, fleet1, intensity1)
    power0 = float(wb['Diesel - DemandSupply']['T30'].value)
    power1 = float(generation.compute_country_annual(p, run, 'ZAF').loc[2024, 'diesel_50ppm'])
    ind = float(industrial.compute_country_annual(p, run, 'ZAF').loc[2024, 'diesel_50ppm'])
    agr = float(agriculture.compute_country_annual(p, run, 'ZAF').loc[2024, 'diesel_50ppm'])
    diesel = {'Power-generation basis': power1-power0,
              'Industrial placeholder added': ind,
              'Agriculture placeholder added': agr,
              'Road vs Excel non-power total': float(road.diesel_50ppm)-(observed['diesel']-power0)}
    jet1 = float(aviation.compute_country_annual(p, run, 'ZAF').loc[2024, 'jet_a1'])
    jet0 = float(wb['fJetFuel']['H24'].value)
    jet = {'Excel regression vs recorded demand': jet0-observed['jet'],
           'Python vs Excel calculation': jet1-jet0}
    lf = p.get('generation', 'load_factor', run).value
    load1 = float(lf[(lf.country == 'ZAF') & (lf.period == 2024)].value.iloc[0])
    results = {
        'year': 2024, 'vintage': '2026', 'scenario': 'high_demand',
        'units': 'litres', 'workbook': str(workbook),
        'petrol': {'observed': observed['petrol'], 'python': float(road.petrol_95), 'effects': petrol,
                   'excel_fleet': fleet0, 'python_fleet': fleet1,
                   'excel_litres_per_vehicle': intensity0, 'python_litres_per_vehicle': intensity1},
        'diesel': {'observed': observed['diesel'], 'python': float(road.diesel_50ppm)+power1+ind+agr,
                   'effects': diesel, 'excel_power': power0, 'python_power': power1,
                   'python_load_factor': load1, 'equivalent_excel_load_factor': load1*power0/power1,
                   'python_road': float(road.diesel_50ppm), 'excel_nonpower': observed['diesel']-power0},
        'jet': {'observed': observed['jet'], 'python': jet1, 'excel_calculated': jet0, 'effects': jet,
                'excel_gdp_per_capita': float(wb['fJetFuel']['F24'].value),
                'excel_passengers': float(wb['fJetFuel']['G24'].value)},
    }
    for fuel in ['petrol', 'diesel', 'jet']:
        r = results[fuel]
        r['residual'] = r['python']-r['observed']-sum(r['effects'].values())
        if abs(r['residual']) > .01:
            raise ValueError(f'{fuel} reconciliation does not tie: {r["residual"]}')
    wb.close()
    output.mkdir(parents=True, exist_ok=True)
    detail.to_csv(output/'vehicle_diagnostics.csv', index=False)
    (output/'driver_reconciliation.json').write_text(json.dumps(results, indent=2)+'\n')
    return results
