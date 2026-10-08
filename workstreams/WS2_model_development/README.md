# WS2 ? Model development

Proposed delivery owner: analyst, paired on complex changes. Accountable lead: Nigel.

Priorities: opening fleet/cohorts, consistent sector accounting, scenario wiring, generation
and refinery operating paths, and agreed regional coverage. Consume WS1 evidence; do not
change assumptions merely to force a historical fit.

Code lives once in `src/lfm/model/` and its adapters; tests live in `tests/`. Record design
choices here or in cross-cutting `docs/methodology/`, not in a duplicate workstream codebase.

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
