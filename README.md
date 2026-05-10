# SACU Liquid Fuels Model

Python rebuild of the Vopak/Reatile liquid fuels supply–demand model.
v1 scope: **SACU** (South Africa, Botswana, Lesotho, Namibia, Eswatini),
**monthly** granularity to **2050**, two coherent scenarios
(`high_demand`, `low_demand`) ported from the original xlsx,
**annual xlsx** as the consumer artifact.

## Why this exists

The original Excel model (`docs/Liquid Fuels Model - Supply Demand, 2025 - Reatile Copy.xlsx`) forecasts South African liquid fuel demand — gasoline, diesel, jet — out to 2050, balances it against domestic refinery supply, and surfaces deficits that imports need to cover. It's been a one-off deliverable: a workbook handed over, then opened the next year and edited in place. That's been getting harder. Three pressures pushed us toward a maintained, code-based rebuild:

- **Annual refresh as a real operational requirement.** Each year's update needs to be reproducible — same inputs producing the same numbers — and stakeholders increasingly ask *"why did the 2030 diesel forecast change vs last year?"* Excel can't decompose that into "assumptions changed" vs "logic changed." A vintaged code-plus-config approach can.
- **Assumptions governance.** A separate central assumptions repo is becoming the team's source of truth for shared inputs (GDP, FX, demographics). The model needs to *consume* assumptions through a clean interface so that swap is mechanical, not a rewrite. That's why everything under `assumptions/<vintage>/` looks the way it does.
- **Geographic expansion.** The xlsx is South Africa only; the practical question is increasingly Southern African — cross-border fuel flows, regional refinery capacity, BLNS as demand satellites. v1 covers SACU; wider SADC is a planned extension, not a v1 scope creep.

This repo is the rebuild. v1 is a **structural baseline** — the architecture, scenario machinery, and ZAF values ported from the xlsx — with the modelling logic itself to be filled in incrementally. The goal: a model the team can refresh annually with a clear contract for what's input vs logic vs output, and a defensible trail back to where every number came from.

## Layout

```
src/lfm/                  Python package
  run.py                  Run = (vintage, scenario, model_version)
  config.py               Path resolution
  core/                   time index, SACU geography, fuel products
  assumptions/            provider abstraction + YAML-directory implementation
  demand/                 vehicles + aviation (modelled), generation + industrial
                          + marine (held), agriculture (deferred)
  supply/                 cross-border + refining-import flows (thin v1)
  output/                 monthly→annual aggregate, template-driven xlsx

assumptions/2026/         the active vintage
  _meta.yaml              vintage metadata + scenario list + xlsx mapping
  macro.yaml              GDP, GDP/capita, growth, population, FX
  vehicles.yaml           S-curve params (high/low), regression coeffs, efficiency paths
  aviation.yaml           jet 2-var regression, passenger driver, product split
  generation.yaml         OCGT capacity, load factor, load shedding, conversion factors
  industrial.yaml         driver-tied growth + seasonality (held)
  marine.yaml             per-port volumes + product split (held)
  agriculture.yaml        deferred placeholder
  supply.yaml             refinery capacities, product mix, utilisation, availability
  seasonality/            CSV-backed monthly indices
  timeseries/             CSV-backed long histories (extracted from xlsx)

scripts/                  ETL / inspection one-offs
  inspect_xlsx.py         dump xlsx structure + named-range values
  extract_xlsx_to_assumptions.py   write xlsx series into timeseries/ CSVs

data/                     raw local working data (gitignored)
runs/                     model outputs, tagged by Run (gitignored)
tests/                    pytest

docs/                     reference material for the original xlsx model
  EV forecast methodology.md
  Liquid Fuels Model - Supply Demand, 2025 - Reatile Copy.xlsx
  24032026fleet-electrification-assumptions-sa-v2200.pptx
  AIA_Vopak_Intermediary_report_vf2_2025.pdf
```

## Install

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Run

```powershell
python -m lfm run --vintage 2026
```

(The CLI is wired but the engine isn't implemented yet — it'll print a
prepared-Run banner and exit cleanly.)

## Tests

```powershell
pytest
```

## What's implemented vs deferred

| Layer | v1 status |
|---|---|
| Package skeleton, CLI, Run/vintage tagging | scaffolded |
| Assumption provider interface | scaffolded |
| Assumption YAMLs (vintaged config, xlsx values ported) | done for ZAF; BLNS = nulls |
| Timeseries CSVs (GDP, OCGT load, refinery utilisation, …) | extracted from xlsx |
| YAML provider implementation | TODO |
| Annual→monthly expansion | TODO |
| Vehicles demand module (MODELLED) | TODO |
| Aviation demand module (MODELLED, regression) | TODO |
| Generation demand module (HELD, OCGT compute) | TODO |
| Industrial / marine (held, driver-tied) | TODO |
| Agriculture | deferred (returns empty frame) |
| Supply flows | thin TODO |
| Annual roll-up + xlsx writer | TODO |

The scaffold defines the seams; filling in the modules above is the v1
build-out. Stub functions raise `NotImplementedError` rather than
returning fake values, so missing pieces fail loudly.

## Reproducibility

Annual refresh means stakeholders will ask "why did this number change
vs last year?" The only durable answer is an **assumption-delta vs
logic-delta** decomposition. That's a design constraint:

- A vintage directory is **immutable** once shipped. Corrections live in
  a new vintage.
- Every run is tagged `(model_version, vintage, scenario)`.
- Year-on-year diffs run new-logic on old-vintage and on new-vintage,
  attributing the gap accordingly.
