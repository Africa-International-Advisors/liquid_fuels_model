# Canon alignment ? 1 October 2026

The user chose a self-contained `pptx/` workspace. The project canon and its generated
instructions now explicitly allow `story/`, `scripts/`, immutable supplied templates,
brand configuration and generated outputs inside that namespace. Only delivered
artifact copies are tracked. The initial migration used the model-only profile. On 1 October 2026 the user
subsequently requested the engagement overlay; `workstreams/` now holds the six-week
workplan, meeting agenda, delivery tracking and analyst learning responsibilities.

Migration: model dimensions/demand/supply moved under `src/lfm/model/`; output helpers
moved to `reporting/`; root scripts moved into `src/lfm/scripts/`; Streamlit Python code
moved under `src/lfm/app/` while deployment files remain in root `app/`. Source workbook,
PowerPoint and PDF moved unchanged to `external/sources/`. Authored notes moved under
`docs/methodology/`. Imports, scripts, application references and Docker entry point
were updated. Old Python import paths are intentionally replaced; use the documented
new package paths and `python -m lfm.scripts.<name>` commands.

A register and exception log were seeded from actual draft inputs. Every value is
unreviewed, not newly verified. Central-engine integration, scenario mapping, inline
legacy assumptions and model validation remain visible exceptions. The CLI preloads
an in-memory provider and records input/code fingerprints. Repeated runs preserve
previous results. The prior model version is retained because calculations are unchanged;
commit and content hashes distinguish this migration.

The presentation toolkit remains an editable local development dependency at version
2.3.0. The source checkout must accompany the environment; a published pinned toolkit
release is still needed for a self-contained installation elsewhere. No client template,
slide mockup, final presentation, peer review or business approval has been invented.


Verification: 54 tests passed, including governance drift/expiry checks and preservation
of prior run outputs. Both scenarios retain exactly the pre-migration demand and balance
values and row ordering. All three original binary reference files are byte-identical.
All three documentation pages pass Streamlit AppTest. Compose configuration parses;
a Docker image rebuild was not run. Governance coverage passes; strict release checking
correctly fails for unreviewed inputs and 43 open exceptions. The presentation prototype
path resolves; template-dependent diagnostics remain pending.


## Subsequent local frontend exception ? 1 October 2026

At the user's explicit request, the documentation viewer now uses the reference
Next.js/TypeScript/Tailwind stack under `frontend/`. The former `src/lfm/app/` and
root `app/` deployment files moved to `archive/2026-10-01_streamlit_viewer/`.
The root Compose files now launch the Next.js viewer. Streamlit is no longer an
active Python dependency. This change is deliberately local: project-canon was not
updated. Earlier Streamlit verification above records the preceding migration state.


Frontend migration verification: production build and TypeScript checks pass; 5 frontend
behaviour tests and the 54 Python tests pass. Live HTTP checks cover all three pages,
static assets, source access, health and unknown-route 404s. The source allowlist rejects
inherited object keys. The standalone production launcher serves locally on 127.0.0.1:3100.
Compose configuration validates; a Docker image build and browser visual review were
not performed. The project-canon content fingerprint is unchanged throughout this frontend
migration. No model execution endpoint, database or published deployment was added.
