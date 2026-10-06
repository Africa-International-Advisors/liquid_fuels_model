# Current Week 1 storyline: Convergence

Open [PDF](Vopak_Week1_Convergence_2026_10_06.pdf) or
[editable PowerPoint](Vopak_Week1_Convergence_2026_10_06.pptx).
This is the current **30-page** storyline. The main story ends with the delivery
roadmap on page 23; the appendix starts on page 24. Previous deliveries remain archived.

The 7 October update adds diesel, jet and petrol input tables at **pages 12?14**,
each with current references, explicit **2030 and 2035 L/M/H** settings and rationale.
These are registered proposed sensitivities, not calibrated or approved forecasts.
The driver dashboard is split into four charts per page (8?9). The trade page has
a compact custom legend; refinery qualifications are retained in notes.

| Agenda | Pages | Purpose |
|---|---|---|
| Overview | 1?3 | Cover, document scope and answer-led summary |
| Market baseline | 4?7 | National accounting, provincial demand and supply allocation |
| Market changes | 8?16 | Drivers, refinery, scenario framework, three fuel lever tables and competing routes |
| Vopak outlook | 17?23 | Footprint, unique deliveries, opportunity, handling, working stock, decision and roadmap |
| Appendix divider | 24 | End of the main story |
| Turnover sensitivity | 25 | Supporting 1/2/3 monthly-turn cases |
| Henry storyboard trace | 26?28 | Responses to every original prompt |
| Closing and palette | 29?30 | Closing page and presentation colours |

Draft inputs and review tasks: [fuel lever handoff](../../../workstreams/WS0_governance/workplan/fuel_lever_review_2026-10-07.md).

Client touchpoints are proposed for weeks 1, 3, 5 and 6, consistent with the
kickoff pack. The later fuel-first instruction takes precedence over the original
Week 1 infrastructure gate. See [workplan review](../../../workstreams/WS0_governance/workplan/convergence_workplan_review_2026-10-06.md).

The storyline remains a draft with explicitly labelled evidence gaps and
illustrations. Consolidation does not resolve those gaps or approve the model.

## Earlier versions

Superseded Convergence v1-v12 and the earlier Analytical Pack are preserved in
[archive/2026-10-06_storyline](archive/2026-10-06_storyline/).
The pre-feedback canonical pair and the local hierarchy revision are preserved in
[archive/2026-10-06_visual-feedback](archive/2026-10-06_visual-feedback/).
Its delivery manifest records verification and hashes. Earlier shipped map and
analytical vintages remain in the existing archive.
The [cleanup manifest](archive/2026-10-06_storyline/cleanup_manifest.json)
records the current pair's SHA-256 hashes and 42 deleted QA exports, each an
exact duplicate of a retained delivered file. Unique QA drafts, review images,
source data, meeting minutes, templates and model runs are preserved.

## Other deliveries

The Manish handover PDF, analyst kickoff, assumption inventory and illustrative
market-envelope files serve separate purposes. They are not alternative current
Week 1 storylines.

## Revision workflow

Use the shared virtual environment. Build a candidate outside delivered:

```powershell
.\.venv\Scripts\python.exe pptx/scripts/build_week1_maps.py --reuse-deck pptx/output/delivered/Vopak_Week1_Convergence_2026_10_06.pptx --output pptx/output/Vopak_Week1_Convergence_candidate.pptx
```

Export its PDF, check the package and visually review it before delivery.
Archive the previous delivered PPTX/PDF pair together, then replace the current
pair under these same stable filenames. Keep candidates and review exports
outside the delivered root. The builder's direct delivery default uses the same
Convergence filename and archives the previous pair before replacement.

See [Manish convergence review](../../../workstreams/WS0_governance/workplan/manish_convergence_2026-10-06.md)
and [Henry question trace](../../../workstreams/WS3_reporting_delivery/henry_verbatim_trace_2026-10-06.md).

The previous 24-page visual-feedback pair is preserved in [archive/2026-10-06_story-corrections](archive/2026-10-06_story-corrections/); its delivery manifest records the updated order, checks and Manish review.

The previous turnover pair is preserved in [archive/2026-10-06_workplan-story](archive/2026-10-06_workplan-story/). That 26-page revision restored working inventory to the main story and adds the kickoff-aligned delivery roadmap.

The previous 26-page pair is preserved in [archive/2026-10-07_fuel-levers](archive/2026-10-07_fuel-levers/), with hashes and validation in its delivery manifest.
