# WS2 ? Model development

Proposed delivery owner: analyst, paired on complex changes. Accountable lead: Nigel.

Priorities: opening fleet/cohorts, consistent sector accounting, scenario wiring, generation
and refinery operating paths, and agreed regional coverage. Consume WS1 evidence; do not
change assumptions merely to force a historical fit.

Code lives once in `src/lfm/model/` and its adapters; tests live in `tests/`. Record design
choices here or in cross-cutting `docs/methodology/`, not in a duplicate workstream codebase.

## 14 October: market-of-interest outlook to 2030 (for Nigel's review)

[`output/delivered/moi_outlook_2026_10_14/`](../../output/delivered/moi_outlook_2026_10_14/) holds a separate annual screen for the six
market-of-interest provinces: `MOI_outlook_model_documentation.docx` (method, assumptions with sources, results, changes from v02 and
limitations), the two scripts (`s13_2025.py`, `moi_forecast.py`), the starting point and results (JSON, CSV). It starts from 2025
demand = production + imports − exports, applies GDP (IMF / Treasury / MTDP), petrol price, efficiency, EVs, rail and Avon peaker
drivers, and reads v02 outputs and repository inputs directly. It is not yet in `src/lfm/`; the changes from v02 are proposals.

## 11 October: directed production planning case

The [v02 analytical workbook](../../output/delivered/sa_analytics_2026_10_11_v02/SA_Fuel_Analytics_2025_Baseline_2026-10-11_v02.xlsx) applies the user's explicit 5.8bn-litre national production assumption. `assumptions/2026/sa_story_case_2025.yaml` is registered separately; the original plant estimate and v01 are preserved. The original estimated product mix is retained provisionally, leaving offsetting petrol and diesel gaps visible. National near-balance does not validate that allocation. The annual scenario screen uses this case; monthly forecast defaults are unchanged.

## 11 October: original South Africa analytical baseline

The [2025 analytical workbook](../../output/delivered/sa_analytics_2026_10_11/SA_Fuel_Analytics_2025_Baseline_2026-10-11_v01.xlsx)
contains the estimated demand allocation, plant supply, 2025–2030 sensitivities and
Mozambique route assessment. [Findings and methods](../../output/delivered/sa_analytics_2026_10_11/analytical_findings.txt)
explain the unresolved national balance. This is a separate annual analytical screen;
it does not replace the monthly forecast or change its defaults.

`sa_analytics_2025.yaml` holds the frozen evidence and authored assumptions under
`EXC-SA-ANALYTICS-202510`. The single cell graph in `model/sa_analytics.py` produces
both model values and Excel formulas. Build with `python -m lfm.scripts.build_sa_analytics`
then the runtime Node executable and `src/lfm/scripts/build_sa_analytics_workbook.mjs`.
The 21.0bn-litre demand estimate and 10.2bn-litre production estimate leave a 4.4bn-litre
availability excess against 2025 customs. That difference is not assumed inventory,
unallocated customer demand or Vopak opportunity. Sources and analyst assumptions
require review before external use; the register expiry is 12 November 2026.

Workbook calculation comparison and visual review were performed. No model tests
were run for this analytics request. Governance coverage passed with 58 open exceptions.

Acceptance: reviewed logic, meaningful regression checks, explained scenario effects and
traceable changes. Preserve the monthly output contract and new-cohort efficiency rule.

WS5 owns the infrastructure and logistics layer. WS2 supplies scenario-tagged demand and production volumes; WS5 adds feasible imports, routes, terminal and storage constraints without duplicating these calculations. See [WS5](../WS5_infrastructure_logistics/README.md).

The [7 October signed-off review audit](../WS0_governance/workplan/sa_review_audit_2026_10_07.csv)
tracks the next implementation work. `src/lfm/model/scenario_levers.py` now provides
explicit-input rail diesel, EV energy-cost/payback, calibrated marginal diversion
and throughput-share calculations. No default coefficients or automatic forecast
integration are implied. EAF/retirement dispatch, annual L/M/H paths, adoption
calibration, route allocation and commercial investment inputs remain open.

The [8 October six-step implementation log](../WS0_governance/workplan/sa_investment_bridge_2026_10_08.csv)
records the investment bridge. `model/investment_bridge.py` provides explicit-input
balance, route economics, capture, working-capacity, break-even and nine-world screens.
Run `python -m lfm.scripts.build_investment_bridge` for the source-hashed baseline report.
The [data request and collection templates](../../output/delivered/investment_bridge_2026_10_08/)
are prepared, not sent. These screens are not wired into forecasts; operating and
commercial calibration and full incremental cash flows remain open.
