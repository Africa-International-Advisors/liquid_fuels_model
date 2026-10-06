# Manish branch review — 6 October 2026

**Outcome: collected and tested; corrections required before integration.**

Reviewed `origin/manish-branch` at `4e64c8c` against Nigel's `main` at
`8e39465`. The branch contains 27 additional commits and changes 136 files.
The common ancestor is `a11b723`. No branch changes have been merged into main.
Nigel's latest presentation styling remains on main.

The isolated local checkout is `runs/review_manish_20261006/`. Paths below
refer to files in that checkout, or on `manish-branch`, unless stated otherwise.
This review is technical and analytical; it does not record business approval.

## What was collected

| Package | Delivered | Remaining gap |
|---|---|---|
| Integrity | 2013 national-sales parser fix; bounded refinery and jet workbook extraction; traced provincial differences | Decide treatment of conflicting 2014/2015 records and incomplete 2018 provincial coverage |
| Source trace | 46-dataset source/file/parser map; public originals for SARS, Stats SA, Sasol and several driver sources | Some originals remain by link or local only; the trace uses the previously delivered engine-use profile |
| Provincial demand | Observed history; clearly labelled 2023–2024 estimates; provincial GDP through 2024 | No new observed provincial fuel sales after 2023 Q1; 2024 national sales remain disputed |
| National balance | Primary SARS annual trade, customs-office and partner extracts; reported operator output in original units | The consolidated balance CSV still uses older trade selections; production, stock changes and sales coverage are not reconciled |
| Drivers and levers | Stats SA monthly activity, quarterly GDP, newer fuel prices; draft 15-lever discussion sheet | Activity-to-litres bridges and scenario definitions remain uncalibrated |

Handback entry point:
`workstreams/WS0_governance/workplan/manish_handback_2026-10-06.md`.
Its delivered deck is
`pptx/output/delivered/Vopak_Manish_Handback_2026_10_06.pdf`.
The handback explicitly says its deck predates the final provincial GDP and
2015 reconciliation updates; it should be refreshed after these review fixes.

## Findings to close

### 1. High priority: rebuild the consolidated balance using the declared primary trade source

`workstreams/WS1_data_validation/fuel_balance_petrol_diesel_2009_2025_2026-10-06.csv`,
lines 17 and 34, still selects rounded government imports and FIASA exports
for 2024. This contradicts the final source decision in
`fuel_balance_2026-10-06.md`, lines 326–331, that SARS is primary from 2014.

For example, selected 2024 diesel imports/exports are 10.800/0.821 bn litres;
the reproducible SARS totals are 10.792547134/0.795834679 bn litres.
The issue is source consistency, not the small rounding difference alone.
The existing balancing requirement and later comparisons therefore are not
outputs of the final declared source selection.

**Manish:** rebuild the balance from the registered SARS extracts from 2014;
keep FIASA and government figures in separate comparison columns. Include
source, unit, period coverage and a reproducible build command. Check that
the selected imports and exports match the primary extract for every year
and product. Recompute the narrative and handback tables from that result.

### 2. High priority: retain the accounting residual as a hypothesis

`fuel_balance_2026-10-06.md`, lines 26–57 and 213–230, calls sales minus net
imports "implied production" and describes petrol as balancing. That quantity
is a balancing requirement; it does not measure production without stock
changes and differences between sales and consumption.

The operator comparison mixes Sasol fiscal years with Astron calendar years,
all-product output with a petrol/diesel question, and an assumed 36 MJ/litre
conversion. The fuel-levy comparison at lines 277–308 uses 11/12 of calendar
sales against an assumed April–February period. These checks support further
investigation, but do not establish an observed 3–4 bn litre diesel
consumption gap. Caveats in the detailed note do not repair the firmer
statement in the handback summary.

**Manish:** label the calculated quantity "sales less net imports — production,
stocks and coverage unresolved". Put operator conversion and levy comparisons
in a separate sensitivity section. Preserve reported units and distinguish
fiscal/calendar years. Use matched monthly periods where available; keep
under-recorded sales as one explanation to test, alongside stocks, product
scope and reporting coverage. Do not replace observed petrol output with the
balancing requirement or adjust national demand for the proposed gap.

### 3. Medium priority: separate BEV and hybrid scenario shares

`workstreams/WS2_model_development/lever_sheet_2026-10-06.md`, lines 74–97,
correctly separates approximately 0.2% BEV sales from 2.8% combined new-energy
vehicle sales, but then proposes "uptake stalls near 3%" for high fuel demand.
It is unclear which category the scenario means. Applying 3% to the model's
BEV adoption curve would treat hybrids as vehicles displacing all liquid fuel
and increase BEV uptake relative to the observed starting point.

**Manish:** give BEV, plug-in hybrid and conventional hybrid separate starting
shares and trajectories. State the denominator (new sales, not total fleet).
Model hybrids through fuel-use/efficiency assumptions and fleet turnover.
Leave the numerical scenario cases proposed until Nigel agrees them.

## Decisions for Nigel, separate from extraction fixes

| Decision | Evidence and consequence | Proposed disposition |
|---|---|---|
| Agriculture/industry baseline replacement | Branch replaces 2024 placeholders with 2021 energy-balance observations in `agriculture.yaml` and `industrial.yaml`. Independent segment calculation gives combined diesel 3.200 → 2.565855 bn L in 2024, a reduction of 0.634145 bn L in both scenarios. The change in 2035 is −0.692403 high / −0.635943 low. | Review sector boundaries and overlap before adopting. Retain `needs_verification`; use a consistent provisional label while review is open. This is a model-input change, not just collection. |
| 2023–2024 provincial estimates | Held 2022 shares; petrol relatively stable, diesel booking shares shift. National 2024 total itself is disputed. One-year historical mean errors are not two-year prediction intervals. | Keep observed history solid and estimates visibly separate; do not present a 2–3% historical average error as a forecast confidence bound. |
| National sales and historical discrepancies | Two FIASA editions disagree; later row duplication is flagged. Department records differ for 2014/2015; 2018 district coverage is incomplete. | Preserve all versions and explicit selection decisions. Do not silently force provincial totals to national sales. |
| Lever calibration | Monthly activity is available, but fuel intensities, haul distances, fleet fuel mix, retirement and mileage are incomplete. | Use the new evidence to improve the SCR charts; agree the activity-to-litres mechanisms before quantifying lever effects. |

## Checks independently completed

- Shared `.venv`, isolated branch checkout, `PYTHONPATH` set to that checkout's
  `src`: full `pytest` run **159 passed** (53.87 seconds).
- `python -m lfm check --vintage 2026`: coverage passed, **52 open exceptions**.
  Outputs remain draft; this is not independent source verification or approval.
- All **34 SARS original workbook hashes** match the branch's evidence record.
- Re-read the originals and reproduced all three SARS CSVs: **235 national,
  2,927 office/mode and 4,347 partner rows**, with matching values and keys.
- Re-read Stats SA originals: all **2,754 monthly observations** match the CSV;
  provincial GDP parser produces **1,728 observations** without warnings.
- Independently calculated agriculture/industry segment changes using the
  main and branch assumption directories and the same unchanged engine.
- No changes under `src/lfm/model/` or to Nigel's SCR builder were found.

Live network refreshes were not rerun; the checks above use committed originals.
Manual transcriptions, remaining linked-only originals and all model parameters
have not received comprehensive independent verification in this review.

## Handback checklist

- [ ] Manish: rebuild primary-source balance CSV and add reconciliation checks.
- [ ] Manish: revise residual wording and separate indicative sensitivities.
- [ ] Manish: clarify BEV/hybrid scenario definitions.
- [ ] Manish: update handback summary/deck to the final evidence and review fixes.
- [ ] Nigel: record decisions on baselines, national sales and estimated provinces.
- [ ] Before integration: bring latest main into `manish-branch`, rerun tests and
  governance, and preserve Nigel's presentation changes. Integrate accepted
  changes only; do not treat this review or a passing check as input approval.

Owners are proposed by the existing workstream responsibilities. Re-review is
triggered by a new branch commit, changed source selection or Nigel's input
decisions; these findings should not be carried into a delivered SCR pack as
resolved until the corresponding actions are complete.
