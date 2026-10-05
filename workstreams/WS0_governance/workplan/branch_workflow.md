# Shared main workflow

Nigel clarified on 5 October 2026 that both Nigel and Manish work directly on
`main`. This supersedes the separate baseline-branch workflow described earlier
that day. Manish pushes his work to `main`; Nigel pulls, reviews, gives feedback,
and pushes corrections to `main`. Both pull before continuing.

## One-time switch: Manish

Commit or stash unfinished work before switching. All work published on
`basecase-2026-10` through commit `dba3a54` is already merged into `main`.
Any newer local or remote commits need to be preserved and reviewed before
bringing them into `main`; do not discard them or overwrite shared history.

```powershell
git status --short
git fetch origin
git switch main
git pull --ff-only origin main
```

If no local `main` exists, use `git switch --track origin/main` instead of
`git switch main`. The old branch is retained for history; no routine merge
from it is required.

## Each morning and before starting work: both people

Start with committed or stashed local work, then:

```powershell
git switch main
git pull --ff-only origin main
```

Manish must pull again after Nigel pushes corrections, before continuing work.
Daily sync is manual; no scheduled pull or message has been set up.

## Before pushing: both people

Commit the intended changes, then pull again to catch the other person's work.
If both have committed since the last pull, preserve both sets of commits with
a merge. Resolve conflicts, run checks on the combined result, and push:

```powershell
git pull --no-rebase origin main
.\.venv\Scripts\python.exe -m lfm check --vintage 2026
.\.venv\Scripts\python.exe -m pytest -q
git push origin main
```

If Git rejects the push because `main` advanced again, repeat the pull, resolve
any conflicts, and rerun relevant checks before retrying. Never force-push.
An unsuccessful fast-forward morning pull means local commits need explicit
reconciliation; use the same merge-and-check process above.

## Published baseline: 5 October 2026

The baseline combines the canonical model layout, governance and Next.js viewer
already on `main` with Manish's source fetchers and staged 2026 datasets.
Fetchers run as `python -m lfm.scripts.<name>`; for example:

```powershell
.\.venv\Scripts\python.exe -m lfm.scripts.refresh_sources --vintage 2026
```

Source-reader packages are pinned in `requirements.txt`. Use the shared `.venv`;
install with `python -m pip install -r requirements.txt`. Editable development
installation is `python -m pip install --no-deps -e .` after installing those pins.
Raw downloads belong in `external/data/raw/`; provided Transnet evidence is in
`external/sources/transnet_tpl_leasing_2026/`.

New source datasets are declared in `assumptions/2026/sources.yaml` and registered
as unreviewed observations. They are not yet adopted by the demand calculations.
The population projection rule and aviation driver proposal now use the existing
governance payload schema. No new scenario or model regression was introduced.

The review found incomplete provincial annual coverage, partial-refresh data loss,
and missing shipped-vintage write guards. These remain owned, time-bounded items
in `governance/exception_log.csv`, alongside source validation and integration.
They must be resolved before the relevant integration/operational refresh triggers.

Publishing this Git baseline does not ship the draft assumption vintage, validate
the model, or record independent review/business approval. See `GATE_CHECKLIST.md`.

Validation: 125 Python tests pass and `python -m lfm check` passes with 50 open
exceptions. Strict checking correctly rejects the unreviewed register and open
exceptions. All nine new source commands load with `--help`, and pinned reader
dependencies import. No live source refresh, source-by-source independent review,
frontend rebuild or website deployment was performed during this integration.
