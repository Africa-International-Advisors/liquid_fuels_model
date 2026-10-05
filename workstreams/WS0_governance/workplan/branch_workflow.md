# Shared baseline and daily branch sync

Agreed by Nigel on 5 October 2026: `main` is the shared integration baseline.
Nigel makes corrections on `main`. Manish continues development on
`basecase-2026-10`, bringing in `main` each morning before starting work.
Daily sync is a manual responsibility; no scheduled pull or message has been set up.

## Each morning: Manish

Start with a clean working tree. Commit completed work first. If unfinished work
must be stashed, use `git stash push -u` and restore it after the merge; retain the
stash until restoration is confirmed. Do not discard changes to make sync pass.

```powershell
git switch basecase-2026-10
git status --short
git fetch origin
git pull --ff-only origin basecase-2026-10
git merge origin/main
```

Resolve any merge conflicts in the baseline branch, then run the checks below
and push `basecase-2026-10`. If the fast-forward pull fails, reconcile local and
remote work explicitly before continuing. Preserve shared history: use merges,
and do not force-push either shared branch.

```powershell
.\.venv\Scripts\python.exe -m lfm check --vintage 2026
.\.venv\Scripts\python.exe -m pytest -q
git push origin basecase-2026-10
```

Pulling only `basecase-2026-10` does not import Nigel's corrections on `main`.
The `git merge origin/main` step is required.

## Corrections and integration: Nigel

Update `main` before editing, commit corrections, validate, and push `main`.
Use a separate checkout/worktree when another branch has unfinished local work.
Review Manish's next increment and merge `basecase-2026-10` into `main` after
resolving paths, assumption-register changes and tests. Manish then repeats the
morning sync to incorporate those corrections.

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
