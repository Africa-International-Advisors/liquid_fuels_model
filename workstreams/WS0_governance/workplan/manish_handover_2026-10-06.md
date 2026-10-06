# Manish handover — 6 October 2026

Today's objective: source and reconcile the South Africa petrol/diesel evidence
before quantifying levers. Track jet separately. Nigel works on `main`; Manish
works on `manish-branch` and returns changes for review before integration.

## 1. Get the latest handover

Run from your repository folder. Commit or stash existing local work first.

If `manish-branch` already exists locally:

```powershell
git fetch origin
git switch manish-branch
git merge origin/main
```

If it exists on the remote but not locally:

```powershell
git fetch origin
git switch --track origin/manish-branch
git merge origin/main
```

If it does not exist locally or remotely:

```powershell
git fetch origin
git switch -c manish-branch origin/main
```

Resolve any merge conflicts before starting. Do not discard existing work or
force-push. See the [branch workflow](branch_workflow.md).

## 2. Open these files

All paths below are relative to your repository folder. Markdown links open the
corresponding local files.

| Open | Exact path | Purpose |
|---|---|---|
| Handover PDF | [pptx/output/delivered/Vopak_Manish_Handover_2026_10_06.pdf](../../../pptx/output/delivered/Vopak_Manish_Handover_2026_10_06.pdf) | Pages 6–7: work-package and driver checklists. Pages 3–5: files, fetch commands and staging. |
| Detailed runbook | [workstreams/WS0_governance/workplan/feedback_focus_2026-10-06.md](feedback_focus_2026-10-06.md) | Exact source paths, public source links, candidate fetch setup and known flags. |
| Meeting record / minutes reference | [workstreams/WS0_governance/meetings/2026-10-06_vopak_standup.docx](../meetings/2026-10-06_vopak_standup.docx) | Received stand-up transcript; consult for meeting context. This is the transcript, not a separately approved set of minutes. |
| Source audit | [output/delivered/Liquid_fuels_source_audit_2026_10_05.xlsx](../../../output/delivered/Liquid_fuels_source_audit_2026_10_05.xlsx) | Start with Direction, Provincial gaps and Repeated keys. |
| Source profile | [output/delivered/source_profile_2026_10_05.html](../../../output/delivered/source_profile_2026_10_05.html) | Inputs, refresh routes and consuming functions. |
| Analytical pack | [pptx/output/delivered/Vopak_Week1_Analytical_Pack_2026_10_06.pdf](../../../pptx/output/delivered/Vopak_Week1_Analytical_Pack_2026_10_06.pdf) | SCR story and the exhibits your evidence will support. |
| Repository rules | [AGENTS.md](../../../AGENTS.md), [CLAUDE.md](../../../CLAUDE.md), [GATE_CHECKLIST.md](../../../GATE_CHECKLIST.md) | Working rules, model architecture and release readiness. |

**Availability:** the stand-up transcript and prior raw-download payload are
currently local to Nigel's machine; they are not on shared `main`. Their links
will not open in a fresh clone until the files are shared. Flag missing originals
and request them from Nigel; do not assume the extracted CSV proves access to
the original. The PDF and runbook are available on `main`.

## 3. Give your LLM this instruction

> Read the repository rules and the dated runbook linked above. Work on
> `manish-branch`. Complete five work packages: data integrity, source
> traceability, provincial petrol/diesel demand beyond 2022, matched
> production/import/export/stock reconciliation, and driver evidence.
> Collect passenger vehicles, freight, agriculture, industry (manufacturing and
> mining separately), power, electrification and GDP/price context. Resolve
> refinery keys/source flags under integrity and fuel-balance work. Use the
> runbook's staging setup before running its per-dataset fetch commands.
> Preserve originals and existing observations; implement and test missing
> retrieval/parsers. Return source files and extracts, resolved/open flags,
> missing evidence with owners and next actions, and test results. Focus on
> evidence today; lever calibration and model integration follow Nigel's review.
> Restore staging environment variables before checking the repository vintage.
> Do not silently replace assumptions or push analyst changes directly to main.

## 4. Return this checklist

- [ ] **Integrity:** old/new values, original source cell/page, reason and
  resolved/open status for completeness, national ties and repeated keys.
- [ ] **Traceability:** publisher -> original -> extract -> consuming function;
  exact paths, units, period, geography and engine-used/staged/reporting status.
- [ ] **Provincial demand:** petrol/diesel by province and period after 2022;
  observed/estimated status, national tie and missing periods.
- [ ] **Fuel balance:** matched product/period/units for production, imports,
  exports and stock movements; residual explained or explicitly open.
- [ ] **Driver evidence:** originals and extracts for all seven driver categories
  on PDF page 7; coverage, revisions and gaps recorded for each series.

Each item returns as ready for review, partial or open. Each open item needs an
owner and next retrieval action. A passing fetch command alone does not establish
source fidelity, completeness or approval to adopt the data.

## 5. Check and publish your branch

Use the shared `.venv`. After restoring staging environment variables, run:

```powershell
.\.venv\Scripts\python.exe -m lfm check --vintage 2026
.\.venv\Scripts\python.exe -m pytest -q
```

Review `git status` and commit only intended code, registered input changes and
review evidence. Follow repository rules for generated artifacts. Preserve
existing vintages and outputs. Fetch/merge current `origin/main` before final
checks if Nigel has published further changes.

```powershell
git push -u origin manish-branch
```

Send Nigel the commit reference, five-package checklist status, test results and
remaining gaps. Nigel reviews accepted input changes before integration into
`main` and before lever quantification. Automated checks do not establish peer
review or business approval.
