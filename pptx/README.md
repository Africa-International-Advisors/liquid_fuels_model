# Liquid fuels presentations

Current review story: **Convergence, 30 pages**, updated 7 October 2026.

- [Current PDF](output/delivered/Vopak_Convergence_current.pdf)
- [Current editable PowerPoint](output/delivered/Vopak_Convergence_current.pptx)
- [Delivery index and evidence status](output/delivered/README.md)
- [Manish review tasks](../workstreams/WS0_governance/workplan/fuel_lever_review_2026-10-07.md)

The main section ends on page 13; appendix starts on page 14. Page 4 covers national sales/trade, page 5 combines provincial geography/history, page 6 shows site-level refinery capacity, and page 7 distinguishes competitive and margin breakpoints.

## File locations

| Location | Contents |
|---|---|
| `output/delivered/` | Current Convergence PDF/PPTX and index |
| [supporting/](output/delivered/supporting/README.md) | Kickoff, assumption inventory, earlier handover and illustration files |
| [archive/](output/delivered/archive/README.md) | Superseded and alternative deliveries, with preserved history |
| `qa/week1_maps/drafts/` | Unshipped local candidates and review exports |
| `story/` | Editorial copy, evidence inventories and illustration definitions |
| `scripts/` | Presentation-only builders; model calculations remain in `src/lfm/model/` |
| `templates/` | Original supplied presentation templates |

Model source-review reports have their own [delivery index](../output/delivered/README.md).
That index links back to these same presentation files; it does not hold duplicate decks.

## Rebuild the latest layout correction

The archived annotated-layout deck is the input to the current correction stage:

```powershell
.\.venv\Scripts\python.exe pptx/scripts/final_review_polish.py pptx/qa/week1_maps/drafts/2026-10-07_review_iterations/Vopak_Week1_Convergence_annotated_layout_2026_10_07.pptx pptx/qa/week1_maps/drafts/Convergence_candidate.pptx
```

The source stages are `annotated_review.py`, `message_titles.py`, `appendix_structure.py`, `analytical_revision.py`, `annotated_layout.py` and `final_review_polish.py`. Each accepts source and destination paths. The annotated-layout stage reads the matching analytical `.revision.json` beside its source deck. Earlier inputs and intermediate evidence are preserved in the dated draft archive.

Build into QA, run package checks, export through PowerPoint and visually inspect. Before replacing the stable delivered filenames, archive the current pair together. Keep only one current pair in `output/delivered/`; update its index and preserve source notes. Original templates remain unchanged.

## Evidence and input status

Observed data, estimates, conditional cases and authored illustrations are
labelled separately. Current L/M/H inputs are proposed sensitivities, not
calibrated forecasts. File consolidation does not imply input or business approval.

The [former presentation README](output/delivered/archive/2026-10-07_delivery-cleanup/presentation_README_before_cleanup.md)
preserves historical build notes. Use this index for current paths and page counts.
