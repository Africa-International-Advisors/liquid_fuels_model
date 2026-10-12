# Agent and analyst working rules

## Shared branch workflow

Nigel works on `main`; Manish creates a named working branch from current
`origin/main`. This is Nigel's clarified workflow of 6 October 2026. Pull or
merge the latest `origin/main` before starting work and before publishing.
Manish pushes his branch for Nigel's review; reviewed changes are integrated
into `main` after governance and relevant checks. Preserve local work and
resolve conflicts. Do not force-push shared history. `basecase-2026-10` is
retained for history, not daily work. See
`workstreams/WS0_governance/workplan/branch_workflow.md` for commands.

Read `CLAUDE.md` for the model architecture and `GATE_CHECKLIST.md` for release readiness.
The repository follows project-canon's model plus engagement profile with the agreed optional `pptx/` workspace.

- Keep calculations under `src/lfm/model/`; resolve file inputs before entering the engine.
- Keep assumptions in vintaged YAML/CSV, not new inline numbers. Declare every input in the register.
- Preserve received files in `external/` and original presentation templates in `pptx/templates/`.
- Keep model scripts in `src/lfm/scripts/` and presentation-only builders in `pptx/scripts/`.
- Model logic must not be duplicated in the presentation workspace.
- Record unresolved inputs and technical limitations with owners and expiry triggers. Do not
  infer verification, peer review or business approval from a passing automated check.
- Preserve shipped vintages and previous run outputs. Run `python -m lfm check` and relevant tests.
- Use the shared `.venv` and `requirements.txt`. Document any editable development dependencies.
- Generated files belong in `runs/`, `output/`, or `pptx/output/`; only delivered artifact copies
  are tracked, under the applicable `output/delivered/` folder.
- Git versions source. Numbered generated pack filenames are allowed to avoid Office locks.
- Do not declare template awareness until the builder uses the supplied master and named layouts.
- No new top-level naming scheme without first updating the canon and this layout contract.


## Engagement workstreams

`workstreams/` holds WS0 governance/planning, WS1 data validation, WS2 model development,
WS3 reporting/delivery, WS4 analyst enablement and WS5 infrastructure/logistics. Start at `workstreams/README.md`.
Root `governance/` remains the model assumption audit trail; WS0 is delivery management.
Model code stays in `src/lfm/`, presentation work stays in `pptx/`, and the weekly cockpit
is a dated record under `workstreams/WS0_governance/workplan/`. Dates and staffing in
the initial six-week plan are proposed, not confirmed commitments.


## Local documentation frontend exception

The user authorised `frontend/` for the Next.js/TypeScript/Tailwind documentation viewer
and explicitly requested no project-canon update for it. This overrides the general
requirement above to update the canon before adding a top-level folder. Keep this
exception local. The viewer reads only its allowlisted Markdown sources; do not add
model execution, assumption editing, a database or a Python API without a new request.
Legacy Streamlit files are archived, not a second active application.

## Approved Vopak presentation layout

For Vopak exhibit/commentary slides, use `pptx/brand_configs/vopak_layout.json`
and the immutable `pptx/templates/Vopak_Approved_Exhibit_Reference_v1.pptx`
(slide 7). The named layout is `Vopak Exhibit + Commentary v1`.
Reuse the native black panel headings, exact panel split, horizontal rules,
circle/arrow divider and numbered navigation; do not recreate them from memory
or reuse the superseded blue-heading evidence layout.
The project extension is `pptx/scripts/lock_vopak_layout.py`; workflow and scope
are documented in `pptx/brand_configs/VOPAK_LAYOUT.md`.
Run its layout check and inspect rendered slides before delivery. Preserve
chart workbooks, approved storyline, native tables, links and previous vintages.
Changing the standard requires explicit user approval and a new contract version.
