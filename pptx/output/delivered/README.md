# Current Week 1 storyline: Convergence

Open [PDF](Vopak_Week1_Convergence_2026_10_06.pdf) or
[editable PowerPoint](Vopak_Week1_Convergence_2026_10_06.pptx).
This is the current 24-page storyline, incorporating the approved visual feedback and document scope. The main story ends on page 17.
Use this pair for review and further revisions; do not create numbered copies
in the delivered root.

| Agenda | Pages | Purpose |
|---|---|---|
| Overview | 1-2 | Cover and answer-led summary |
| Market baseline | 3-6 | National accounting, provincial demand and supply allocation |
| Market changes | 7-11 | Demand drivers, supply cases, forecasting and competing routes |
| Vopak outlook | 12-17 | Customer flows, footprint, opportunity gates and inventory sensitivity |
| Appendix divider and scope | 18-19 | Clear story ending; what the document covers and does not establish |
| Henry storyboard trace | 20-22 | Responses to every original storyboard prompt |
| Closing and palette | 23-24 | Closing page and presentation colours |

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
