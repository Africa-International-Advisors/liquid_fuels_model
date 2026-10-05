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
