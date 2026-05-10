# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This repo is the Python rebuild of the Vopak/Reatile liquid fuels supply–demand model. v1 scope: **SACU** (ZAF, BWA, LSO, NAM, SZW), **monthly** to **2050**, **two coherent scenarios** (`high_demand`, `low_demand`) ported from the original xlsx, **annual xlsx** as the consumer artifact.

The original Excel artifacts live under `docs/` as **reference documents only** — do not treat them as the model:

- `docs/Liquid Fuels Model - Supply Demand, 2025 - Reatile Copy.xlsx` — original xlsx model
- `docs/EV forecast methodology.md` — methodology note for the original xlsx (S-curve, GDP regression, stock build-up)
- `docs/24032026fleet-electrification-assumptions-sa-v2200.pptx`, `docs/AIA_Vopak_Intermediary_report_vf2_2025.pdf` — deliverables

## Architecture (read this before editing)

```
src/lfm/
  run.py            Run dataclass — (vintage, scenario, model_version) is the
                    unit of reproducibility; every output carries this triple
  config.py         Path resolution; env vars LFM_ASSUMPTIONS_DIR / LFM_DATA_DIR
                    / LFM_RUNS_DIR override defaults
  core/             dimensions every dataframe is keyed on
    time.py         monthly + annual PeriodIndex; ExpansionRule for annual→monthly
    geography.py    SACU country list — adding a country requires explicit scope change
    products.py     fuel product taxonomy
  assumptions/
    base.py         AssumptionProvider Protocol — the seam between model and
                    assumption sources
    yaml_provider.py YamlDirectoryProvider — reads assumptions/<vintage>/
  demand/
    base.py         DemandSegment Protocol; SegmentStatus = MODELLED|HELD|DEFERRED
    vehicles.py     MODELLED  (S-curve EV + GDP-driven new vehicles)
    aviation.py     MODELLED  (xlsx 2-var jet regression on GDP/capita + pax)
    generation.py   HELD      (OCGT capacity x load factor; ports xlsx OCGT compute)
    industrial.py   HELD      (driver-tied growth)
    marine.py       HELD      (per-port volumes + product split)
    agriculture.py  DEFERRED  (returns empty frame)
  supply/flows.py   thin balancing layer (SA refining vs imports vs BLNS demand)
  output/
    aggregate.py    monthly→annual roll-up
    xlsx.py         template-driven workbook writer

assumptions/<vintage>/   vintaged config — the contract is the YAML schema
  _meta.yaml             vintage metadata + scenario list + xlsx mapping
  <domain>.yaml          per-domain assumption files (macro, vehicles, aviation,
                         generation, industrial, marine, agriculture, supply)
  seasonality/*.csv      monthly indices (avg to 1.0)
  timeseries/*.csv       long histories referenced from YAMLs
                         (extracted from xlsx via scripts/extract_xlsx_to_assumptions.py)

scripts/                 ETL / inspection one-offs
  inspect_xlsx.py        dump xlsx structure + named-range values
  extract_xlsx_to_assumptions.py  write xlsx series into timeseries/ CSVs
```

## Three load-bearing design decisions

These are the architectural commitments you should not casually reverse:

1. **Assumptions live behind a provider interface, not inline.** The model never reads YAML directly — it asks the `AssumptionProvider`. This is what lets the central assumptions repo replace the local YAML directory later without touching model code. Do not embed numbers in `src/lfm/`.

2. **Vintage directories are immutable once shipped.** Corrections open a new vintage. This is the only way the year-on-year "why did the number change" question stays answerable. `_meta.yaml` carries `status: draft|shipped|superseded`.

3. **Internal model is monthly; consumer xlsx is annual.** The aggregation lives in `output/aggregate.py`. Don't make the engine annual to "match" the xlsx — the held segments need monthly seasonality and that lives at the engine layer.

4. **Vehicle fuel-efficiency improvement applies to new sales only, not the whole fleet.** Each new-vehicle cohort enters at the year-of-manufacture L/100km (`fuel_consumption` baseline × cumulative `efficiency_improvement`) and that figure is held for the cohort's life. Fleet-average L/100km in a given year is a stock-weighted sum across cohorts. This is an explicit modelling rule recorded in `vehicles.yaml::fuel_consumption` — it implies the vehicles compute must track stock by cohort (year of first registration), not as a single bulk number.

## v1 build-out priorities

The scaffold is in place; stub functions raise `NotImplementedError`. The build order that respects dependencies:

1. `assumptions/yaml_provider.py` — load YAML + referenced CSVs into `Assumption` objects.
   Scenario filtering on the timeseries CSVs (`scenario in {run.scenario, "shared"}`)
   happens here.
2. `core/time.py::expand_annual_to_monthly` — flat / linear / seasonal rules
3. `demand/vehicles.py` — S-curve + new-vehicle regression (coeffs in vehicles.yaml)
4. `demand/aviation.py` — apply the 2-var jet regression (coeffs in aviation.yaml)
5. `demand/generation.py` — OCGT compute (capacity × load_factor → diesel litres)
6. `demand/{industrial,marine}.py` — held segments share a tight pattern
7. `output/aggregate.py` then `output/xlsx.py`
8. `supply/flows.py` — thin demand-vs-refining balance using `supply.yaml`

## Working in this repo

- **Don't reproduce the xlsx cell-for-cell.** This is a clean-slate redesign — fidelity to the xlsx outputs is not a requirement. Use it as documentation, not a target.
- **Don't add countries beyond SACU** without an explicit scope change. Wider SADC is a planned future extension.
- **Stub functions raise rather than return fake values** so missing pieces fail loudly. Preserve that discipline.
- **The xlsx is a *report*, not the model.** Use openpyxl with a template; don't build workbooks cell-by-cell from scratch in code.

## Commands

```powershell
# install (editable)
pip install -e ".[dev]"

# run the (currently no-op) engine
python -m lfm run --vintage 2026

# tests
pytest

# single test
pytest tests/test_smoke.py::test_sacu_is_five_countries

# lint
ruff check src tests
```

## What lives where for assumptions

When you need to know "where does X come from?":

- **Code-side default / fallback?** Nowhere — the model has no fallbacks; every input flows from the provider.
- **Per-vintage config value?** `assumptions/<vintage>/<domain>.yaml`
- **Long historical / forecast series?** `assumptions/<vintage>/timeseries/*.csv`, referenced by `csv:` field in the YAML.
  CSV schema is `(country, period, scenario, value)` long-format. `scenario=shared` means the row applies to all scenarios.
- **Monthly seasonal pattern?** `assumptions/<vintage>/seasonality/*.csv`, referenced by name in the segment YAML
- **Raw upstream data (pre-cleaning)?** `data/raw/`, gitignored — not part of any vintage
- **Re-extracting xlsx values into a new vintage?** `python scripts/extract_xlsx_to_assumptions.py`
  rewrites the timeseries CSVs from the xlsx. Pair with manual updates to the segment YAMLs for any new scalars / coefficients.

## Scenarios

v1 carries two coherent scenarios from the original xlsx:

- `high_demand` — high GDP growth, slow EV penetration (`EV_Low_Penetration`),
  low fuel-efficiency improvement, high load shedding. The "more liquid fuel needed" worldview.
- `low_demand` — low GDP growth, fast EV penetration (`EV_High_Penetration`),
  high fuel-efficiency improvement, low load shedding.

The full xlsx-to-scenario mapping lives in `assumptions/2026/_meta.yaml::xlsx_scenario_mapping`.
The naming reflects what's downstream of the assumption (fuel demand), not the
direction of any single input — keep that in mind when adding new assumption keys.
