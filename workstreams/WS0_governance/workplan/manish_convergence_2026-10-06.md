# Week 1 story convergence with Manish 6 October 2026

Nigel has agreed to use the collected evidence to update the Week 1 South
Africa story. The convergence draft leads with national accounting, then
provincial demand, drivers, refinery scenarios and customer accessibility.
Manish should align the data handback with this story before integrating
model-input changes.

## Open these files

All files below are tracked and available after merging current `origin/main`.

| File | Purpose |
|---|---|
| [Updated Week 1 PDF](../../../pptx/output/delivered/Vopak_Week1_Convergence_2026_10_06_v11.pdf) | The 22-page draft: overview, market baseline, market changes and Vopak outlook |
| [Editable PowerPoint](../../../pptx/output/delivered/Vopak_Week1_Convergence_2026_10_06_v11.pptx) | Same story with editable charts and clickable navigation |
| [Branch review](../../WS1_data_validation/manish_branch_review_2026-10-06.md) | Findings against `manish-branch` at `4e64c8c`; checks and baseline decisions |
| [Morning handover](manish_handover_2026-10-06.md) | Original five-package objective: evidence before lever quantification |
| [Morning meeting record](../meetings/2026-10-06_vopak_standup.docx) | Received stand-up transcript; meeting context, not separately approved minutes |
| [Reporting evidence manifest](../../../pptx/story/evidence_2026_10_06/manifest.json) | Exact source paths, branch reference and SHA-256 for the reporting copies |

## Story structure

1. **Overview (page 2):** lead with the current answer, group rows by the agenda and retain S/C/R pills and Henry's resolution questions; link to the deep dives.
2. **Market baseline (pages 3?6):** national accounting first, then observed provincial demand and supply origin. Separate measured, estimated and illustrative values.
3. **Market changes (pages 7?11):** historical drivers and refinery change, then the forecast framework and route competition. Forecasts must connect assumptions to annual fuel demand and supply, with uncertainty explicit.
4. **Vopak outlook (pages 12?17):** access and unique flows, regional opportunity and assets, then where to play, how to win and when to act. Inventory sensitivity follows the decision gates.

Pages 18?20 respond to every Henry storyboard prompt, with partial/open status and linked evidence. Page 21 closes the pack; page 22 is the palette appendix. Chevrons link to the first page of each section (2, 3, 7, 12). The forecast framework establishes the analysis sequence; it does not add calibrated fuel forecasts.

## What is agreed for the draft

| Page | Updated story and figures | What remains to converge |
|---|---|---|
| 2 | SCR overview links to the reordered deep dives | Keep overview and deep dives consistent |
| 3 | SARS 2024 diesel imports 10.792547134 bn L; exports 0.795834679; net imports 9.996712456. Petrol imports 4.000854433; exports 0.919745016; net imports 3.081109418. Combined net imports 13.077821873. | Rebuild the balance CSV using this primary trade selection; retain alternative sources as comparisons |
| 3 | Reported sales remain petrol 9.029 / diesel 11.734 bn L, combined 20.763, flagged as unverified | Resolve FIASA editions and period coverage; do not silently adopt these as verified consumption |
| 3 | Sales less net imports is 7.685178127 bn L | Label as a balancing requirement; match actual production, stocks and sales coverage. Do not add a proposed 3–4 bn L gap to demand |
| 4–5 | Observed provincial map/history remains 2022; separate 2024 petrol estimates include Gauteng 3.47, KZN 1.47 and Western Cape 1.41 bn L | Estimates hold 2022 shares and inherit uncertainty in the national total. Retain observed/estimated fields and do not imply later observed sales |
| 7 | Freight annual history extended; mining/manufacturing use production indices; complete-year prices extend to 2025. Monthly activity to July 2026, quarterly GDP to Q2 2026 and inland prices to October 2026 are staged | Charts use complete years; distinguish YTD and monthly evidence. Keep BEV/PHEV/conventional hybrids separate; define fuel intensities before estimating litre effects |
| 8 | Capacity scenarios remain conditional. Actual FY2024 output: Secunda 29.1 and Natref 17.8 million barrels, the latter Sasol's share | Check source pages; fiscal vs calendar year, ownership and all-product scope must be explicit. Source product yields before deriving imports |
| 9–14 | Accessibility, customer-volume and storage examples remain conditional | National trade is not Vopak market share. Close route costs, usable capacity, customer rights and unique deliveries before sizing capture |
| 16 | Market outlook: where to play, how to win, when to act and conditions for Durban, Lesedi and competing gateways | Priorities are hypotheses. Return named customers, route economics, usable capacity, commercial rights and conditional timing |
| 17 | Preliminary inventory sensitivity follows the outlook | Secure incremental flows and identify a usable-capacity gap before sizing new tanks |

The reporting copies are under `pptx/story/evidence_2026_10_06/`. They consume
the collected observations without replacing engine inputs. The agriculture
and industry baseline changes remain a separate Nigel decision. The analyst
branch has not been merged wholesale into main.

Overview rows are numbered S1, S2, S/C3, C4, C5, R6 and R7. Every analytical page title begins with its matching row references; the Overview chevron links back to page 2; page 9 supports both rows 3 and 4.

## Henry storyboard coverage

Start with [Henry's verbatim wording and evidence trace](../../WS3_reporting_delivery/henry_verbatim_trace_2026-10-06.md). It maps every source prompt on slides 30?32 to the current response and deck pages; exact words are also in the appendix speaker notes.

The opening answer is that imports are material, but Vopak growth depends on accessible customer flows. The agenda-led summary is on page 2; every prompt from received storyboard pages 30?32 has a current response on pages 18?20. The exact response register is [henry_question_answers_2026_10_06.json](../../../pptx/story/henry_question_answers_2026_10_06.json). Partial/open responses are explicit gaps, not completed analyses. Review Mossgas dates/status, vehicle efficiency, rail participation, price/mileage response, plant mechanisms, fleet penetration and import growth/entry ports before closing those prompts.

## What Manish must do next

- [ ] Rebuild the national balance from SARS primary trade from 2014 onward.
  Preserve FIASA/government alternatives, source/period/unit fields and a
  repeatable build command. Add checks for selected trade against its extract.
- [ ] Rewrite the residual narrative: production, stocks and coverage are
  unresolved. Separate fiscal/calendar operator sensitivities and fuel-levy
  comparisons from matched accounting. Keep original operator units.
- [ ] Review the figures and labels on pages 3, 5, 7 and 8 against originals.
  Return corrections with the original page/cell, old/new value and reason.
- [ ] Use page 9 to propose the forecast specification: target fuel/region, horizon, observed history, baseline growth, lever mechanisms, alternative cases, validation and uncertainty. Keep assumptions in registered vintaged files; distinguish proposals from accepted inputs.
- [ ] Define BEV, PHEV and conventional-hybrid cases separately. State whether
  each share is new sales or stock; show the fleet-turnover and fuel-use bridge.
- [ ] Refresh the handback summary and deck to include provincial GDP, traced
  2015 discrepancies and these review outcomes. Return ready/partial/open
  status for each of the morning's five packages.
- [ ] Return a distinct proposal for agriculture/industry baseline acceptance,
  with segment overlap and forecast effects. Do not interpret the story update
  as approval of those engine inputs or of lever calibration.

## Commands and LLM instruction

Commit existing work first, then run from the repository root:

```powershell
git fetch origin
git switch manish-branch
git merge origin/main
.\.venv\Scripts\python.exe -m lfm check --vintage 2026
.\.venv\Scripts\python.exe -m pytest -q
```

Give the LLM this instruction:

> Read the morning handover, branch review and this convergence checklist.
> Work on manish-branch. Preserve Nigel's reordered story and presentation
> styling. Rebuild the national balance using SARS as primary trade from 2014,
> retaining other sources in comparison columns. Distinguish measured output
> from the balancing requirement and indicative sensitivities. Review the
> exhibit numbers against originals and resolve BEV/hybrid scenario definitions.
> Keep provincial estimates separate from observations and return baseline
> changes as an explicit decision for Nigel. Implement and test the needed
> data/reporting corrections; update the handback. Return commit, checks,
> changed values and ready/partial/open status. Do not merge into main or
> calibrate scenarios on unapproved inputs.

After changes, bring in any newer main updates, repeat checks and publish:

```powershell
git fetch origin
git merge origin/main
.\.venv\Scripts\python.exe -m lfm check --vintage 2026
.\.venv\Scripts\python.exe -m pytest -q
git push origin manish-branch
```

Return the branch commit, the five-package checklist and the exhibit correction
list. Nigel will review the combined result before model integration.

The current draft passed PowerPoint package/off-canvas checks and was exported
and visually reviewed. The branch review recorded 159 passing tests and 52
open governance exceptions; those checks do not establish input approval.
