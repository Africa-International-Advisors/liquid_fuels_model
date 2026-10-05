# SACU Liquid Fuels Model

`main` is the shared baseline; Manish continues on `basecase-2026-10` and brings
in corrections from `main` each morning. See the
[branch workflow](workstreams/WS0_governance/workplan/branch_workflow.md).

The 5 October source datasets and fetchers are included, with source observations
registered as unreviewed. Their adoption into demand calculations remains pending.

Python rebuild of the Vopak/Reatile liquid-fuels model. Intended scope: SACU,
monthly demand from 2024 to 2050, with annual supply balances and two scenarios.
Current populated country coverage is South Africa only. Outputs are provisional.

## Why this exists

The decision question is: how much liquid fuel will SACU need, how much can domestic
production supply, and what gap remains under different scenarios? The rebuild
separates assumptions, calculations and reporting so annual changes can be explained.
A national deficit is not yet a terminal-throughput or trade-routing forecast.

## Install and run

Use Python 3.14 for the pinned, tested environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m lfm check --vintage 2026
.\.venv\Scripts\python.exe -m lfm run --vintage 2026 --scenario high_demand
.\.venv\Scripts\python.exe -m lfm run --vintage 2026 --scenario low_demand
.\.venv\Scripts\python.exe -m pytest
```

`lfm check` checks governance coverage and drift, not model validity. `lfm check --strict`
also fails while exceptions remain open. Exceptions expire on 12 November 2026 or
before formal release, whichever comes first. Unknown confidence and source dates
remain explicit; the register does not certify legacy assumptions.

## Layout

```text
src/lfm/
  model/          demand, supply and shared dimensions; no file I/O
  assumptions/    file-backed and in-memory provider adapters
  governance.py   register coverage, drift and exception checks
  reporting/     aggregation and future Excel reporting
  scripts/       workbook extraction, inspection and reconciliation
  cli.py, run.py  orchestration and run identity
assumptions/2026/ versioned YAML and CSV inputs (draft)
governance/      individually owned input rows and time-bounded exceptions
external/        original workbook, received reports and source data
docs/            authored methodology and working notes
runs/            calculated results and provenance (ignored)
output/          generated model reports; delivered/ copies tracked
pptx/            separate presentation workspace (see pptx/README.md)
frontend/        Next.js / Tailwind read-only documentation viewer (local exception)
workstreams/     engagement workplan, delivery tracking and analyst learning
tests/           model, governance and migration checks
archive/         superseded material when needed
```

## Current implementation

Vehicles, aviation, generation, industrial, marine and agriculture compute demand.
Supply and demand-supply balances run; annual aggregation and CSV reporting work.
Vehicle assumptions and several sector baselines remain provisional. The Excel writer
is still a stub. BLNS data, central assumptions-engine integration, independent review
and business sign-off are not complete. See `GATE_CHECKLIST.md` and the exception log.

The primary demand modules compute annually and expand to monthly rows; realistic
monthly seasonality remains a modelling task. Historical reconciliation has material
gaps. Tests passing does not mean the forecasts are ready for decisions.

## Documentation viewer

The read-only Next.js/TypeScript/Tailwind viewer follows the frontend stack used in
`tender_scraper`. It reads the overview, hypothesis tree and architecture directly from
Markdown. It does not execute the model or edit assumptions. Project-canon was not
changed for this frontend; it is an explicit local exception.

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

Open http://127.0.0.1:3100. From the repository root, `docker compose up -d --build`
provides the same viewer. See `frontend/README.md` for build and deployment instructions.
The former Streamlit implementation is preserved in `archive/2026-10-01_streamlit_viewer/`.

## Reproducibility

A run records model version, Git commit, dirty-worktree status, source-code hashes,
input/governance hashes, scenario, vintage, execution user, time and open exceptions.
Existing run outputs are not overwritten: repeated executions create a timestamped
subfolder under the tagged run directory. Shipped vintages must not be edited.
The central-engine snapshot reference is explicitly null until that integration exists.

## Reference tools

```powershell
python -m lfm.scripts.compare_history
python -m lfm.scripts.verify_against_xlsx
```

The original workbook is in `external/sources/` and remains read-only. Extraction is
`python -m lfm.scripts.extract_xlsx_to_assumptions`; it updates the draft inputs and
therefore requires deliberate reconciliation with the governance register afterwards.

## Presentation workspace

The agreed canon exception keeps `pptx/story/`, `pptx/scripts/`, original templates,
brand settings and workflow together. Builders consume stamped model results and do
not duplicate model logic. The user's template and an approved slide mockup are still
pending; the presentation is not build-ready. See `pptx/README.md`.


## Engagement workstreams

`workstreams/` holds WS0 governance/planning, WS1 data validation, WS2 model development,
WS3 reporting/delivery and WS4 analyst enablement. Start at `workstreams/README.md`.
Root `governance/` remains the model assumption audit trail; WS0 is delivery management.
Model code stays in `src/lfm/`, presentation work stays in `pptx/`, and the weekly cockpit
is a dated record under `workstreams/WS0_governance/workplan/`. Dates and staffing in
the initial six-week plan are proposed, not confirmed commitments.
