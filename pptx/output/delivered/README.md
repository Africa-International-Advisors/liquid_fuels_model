# Current Week 1 storyline: Convergence

Open [PDF](Vopak_Week1_Convergence_2026_10_06.pdf) or
[editable PowerPoint](Vopak_Week1_Convergence_2026_10_06.pptx).
This is the current 26-page storyline, aligned to the kickoff workplan and the
approved sequence. The main story ends with the delivery roadmap on page 19.
Use this pair for review; previous deliveries are archived together.

| Agenda | Pages | Purpose |
|---|---|---|
| Overview | 1-3 | Cover, document scope and answer-led summary |
| Market baseline | 4-7 | National accounting, provincial demand and supply allocation |
| Market changes | 8-12 | Drivers, supply cases, scenarios and competing routes |
| Vopak outlook | 13-19 | Regional footprint, customer opportunity, handling, working stock, decision and delivery gates |
| Appendix divider | 20 | Clear end of the main story |
| Turnover sensitivity | 21 | Supporting 1/2/3 monthly-turn cases |
| Henry storyboard trace | 22-24 | Responses to every original prompt |
| Closing and palette | 25-26 | Closing page and presentation colours |

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

The previous turnover pair is preserved in [archive/2026-10-06_workplan-story](archive/2026-10-06_workplan-story/). The current 26-page pack restores working inventory to the main story and adds the kickoff-aligned delivery roadmap.
