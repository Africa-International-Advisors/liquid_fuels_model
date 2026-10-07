# Liquid fuels presentations

The current review story is **Convergence, 31 pages**, updated 7 October 2026.

- [Current PDF](output/delivered/Vopak_Week1_Convergence_2026_10_06.pdf)
- [Matching editable PowerPoint](output/delivered/Vopak_Week1_Convergence_2026_10_06.pptx)
- [Manish review tasks](../workstreams/WS0_governance/workplan/fuel_lever_review_2026-10-07.md)
- [Delivery index](output/delivered/README.md)

The stable filenames retain the Week 1 date, 6 October. Latest changes include
2030/2035 fuel lever proposals on pages 12-14 and legends above the driver
plots on pages 8-9. Page 24 sets out Manish’s five priorities, expected outputs
and Nigel’s review decisions. The main story ends there; appendix starts on page 25.

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

## Rebuild the current story

Use the shared virtual environment and build a candidate outside delivered:

```powershell
.\.venv\Scripts\python.exe pptx/scripts/build_week1_maps.py --reuse-deck pptx/output/delivered/Vopak_Week1_Convergence_2026_10_06.pptx --output pptx/output/Vopak_Week1_Convergence_candidate.pptx
```

Run package checks, export through PowerPoint and visually inspect the PDF.
Preserve the previous delivered pair together in a dated archive before replacing
the stable filenames. Update the delivery index when page count or scope changes.
Move completed local candidates into QA drafts; keep the delivered top level clear.

The builder uses the supplied Vopak master and named layouts. The preserved
53-slide kickoff reference is now under `output/delivered/supporting/`; its
builder and `deck.yaml` write there too. `deck.yaml` is the kickoff project,
while `build_week1_maps.py` builds the current Convergence story.

## Evidence and input status

Observed data, estimates, conditional cases and authored illustrations are
labelled separately. Current L/M/H inputs are proposed sensitivities, not
calibrated forecasts. File consolidation does not imply input or business approval.

The [former presentation README](output/delivered/archive/2026-10-07_delivery-cleanup/presentation_README_before_cleanup.md)
preserves historical build notes. Use this index for current paths and page counts.
