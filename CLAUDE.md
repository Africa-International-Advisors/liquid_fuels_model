# Liquid fuels model conventions

## What this repo is

A provisional SACU liquid-fuels forecast, currently populated for South Africa only.
Owner: nigel.zhuwaki. Active vintage: 2026 (draft). Forecast horizon: 2024?2050.
Decision question: what fuel demand and domestic supply gaps arise under high and low
liquid-fuel demand scenarios? This is not yet a port-routing or terminal-throughput model.

## Architecture

Follow the project-canon model plus engagement profile and its optional `pptx/` workspace.
- `src/lfm/model/`: demand, supply and dimension calculations; no file/network I/O.
- `src/lfm/assumptions/`: provider adapters. The CLI preloads an in-memory snapshot.
- `src/lfm/governance.py`: mechanically checks inputs against the register and exceptions.
- `src/lfm/reporting/`: shared output transformations and model report builders.
- `src/lfm/scripts/`: extraction, inspection and reconciliation commands.
- `frontend/`: read-only Next.js/TypeScript/Tailwind documentation viewer; local exception,
  not an addition to project-canon. No FastAPI service or model-run UI is included.
- `assumptions/<vintage>/`: declared inputs, immutable once shipped.
- `governance/`: owned register rows and dated exceptions; no fabricated validation.
- `external/`: received material, preserved unchanged.
- `docs/methodology/` and `docs/notes/`: authored explanation and working notes.
- `runs/`: calculated outputs and provenance, ignored by Git.
- `output/`: built model reports; only `delivered/` copies tracked.
- `pptx/`: presentation-only workflow; `story/` for content, `scripts/` for builders,
  `templates/` for original supplied files, `brand_configs/` for styling,
  `output/` for generated packs (only `delivered/` tracked), `qa/` for generated checks.
- `archive/`: superseded material, not a second active structure.

## Load-bearing design decisions

1. Inputs are accessed through the provider. Do not embed new modelling assumptions in code.
2. Preserve shipped vintages. Draft changes must update the register and appropriate exceptions.
3. Demand output is monthly; annual reporting aggregates it. Supply currently computes annually.
4. Vehicle efficiency improvements apply to new cohorts, not to the whole fleet retroactively.
5. Do not reproduce the workbook cell-for-cell. Explain intentional methodology changes.
6. Do not add countries beyond SACU without an explicit scope change.
7. Presentation builders consume results, not a duplicate model. Never hand-edit generated packs.

## v1 build-out priorities

Validate opening vehicle stock and sector baselines; resolve historical reconciliation;
review scenario wiring; source agreed regional coverage; integrate the shared assumptions
engine; finish template-based Excel reporting; complete independent review and sign-off.
These are model-development tasks, not completed by the structural migration.

## Working in this repo

Read AGENTS.md and GATE_CHECKLIST.md. Run governance and relevant tests after changes.
New input scalars and CSV observations require owned register rows; structured blocks
inherit a register group. All exceptions need a reason, owner, expiry and migration path.
No unknown source date, confidence or approval is to be invented. Open exceptions mean
provisional output. `lfm check` passing establishes coverage, not release approval.
Existing outputs are preserved; repeated runs use timestamped subfolders.

## Scenarios

`high_demand`: higher growth, slower EV adoption and more OCGT demand.
`low_demand`: lower growth, faster EV adoption and less OCGT demand.
The exact workbook mappings are in `assumptions/2026/_meta.yaml`.
Scenario definitions are local; central mapping is an explicit open exception.

## What lives where for assumptions

YAML declares scalars and structured settings; referenced CSVs carry series.
`governance/assumption_register.csv` records each scalar/observation and its inherited
source, owner and review status. `governance/exception_log.csv` records unresolved blocks
and integration limitations. See `governance/README.md` for the update process.

## Commands

```powershell
python -m lfm check --vintage 2026
python -m lfm check --vintage 2026 --strict
python -m lfm run --vintage 2026 --scenario high_demand
python -m pytest
python -m lfm.scripts.compare_history
python -m lfm.scripts.verify_against_xlsx
npm.cmd --prefix frontend run dev
.\.venv\Scripts\brand-pptx.exe doctor --strict
```

The final command intentionally reports incomplete presentation setup until the user
supplies the template and the builder is configured after mockup review.


## Engagement workstreams

`workstreams/` holds WS0 governance/planning, WS1 data validation, WS2 model development,
WS3 reporting/delivery and WS4 analyst enablement. Start at `workstreams/README.md`.
Root `governance/` remains the model assumption audit trail; WS0 is delivery management.
Model code stays in `src/lfm/`, presentation work stays in `pptx/`, and the weekly cockpit
is a dated record under `workstreams/WS0_governance/workplan/`. Dates and staffing in
the initial six-week plan are proposed, not confirmed commitments.
