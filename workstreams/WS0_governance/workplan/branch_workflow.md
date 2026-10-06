# Main and analyst branch workflow

Nigel clarified on 6 October 2026: Nigel works on `main`; Manish creates a
named working branch from current `origin/main`. This supersedes the 5 October
instruction that both people push directly to main. The historical baseline
branch is retained; it is not the daily analyst branch.

## Nigel on main

Preserve local work, then pull before starting and before publishing:

```powershell
git switch main
git pull --ff-only origin main
```

Commit only the intended files. Run governance and relevant tests before pushing
main. Never force-push. If origin/main has advanced, merge and resolve conflicts,
then repeat the checks on the combined result.

## Manish creates a branch

Commit or stash existing work first. Use a descriptive name such as
`manish/data-validation-2026-10-06`:

```powershell
git fetch origin
git switch -c manish/data-validation-2026-10-06 origin/main
```

If the branch already exists, switch to it rather than recreating it. During work,
bring Nigel's latest updates into the analyst branch:

```powershell
git fetch origin
git merge origin/main
.\.venv\Scripts\python.exe -m lfm check --vintage 2026
.\.venv\Scripts\python.exe -m pytest -q
```

Resolve conflicts and commit intended changes. A commit message must explain the
problem, changed values/logic, source evidence, checks and remaining limitations.
Publish the analyst branch, not main:

```powershell
git push -u origin HEAD
```

Nigel reviews the branch or pull request and integrates accepted changes into main.
Run governance and relevant tests on the integrated result before publishing main.
Do not infer data approval from a successful merge or automated check. No branch
has been created on Manish's behalf by this documentation update.

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
