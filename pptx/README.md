# Liquid fuels presentations

Current South Africa review: **v27, 43 pages**, updated 8 October 2026.

- [Current PDF](output/delivered/supporting/SA_Market_Story_2026-10-08_v27.pdf)
- [Current editable PowerPoint](output/delivered/supporting/SA_Market_Story_2026-10-08_v27.pptx)
- [Delivery index and evidence status](output/delivered/README.md)
- [Page guide and outstanding inputs](output/delivered/supporting/README.md)
- [Manish's next handback](../workstreams/WS0_governance/workplan/sa_review_milestone_2026_10_08.md)

The appendix starts at page 19. Sector charts are on page 8, the Durban–Lesedi issue tree
on page 16, outstanding requests on page 18, vehicle calibration on page 26 and power
fleet/cases on page 33. Scenario and commercial calibration remain open.

## File locations

| Location | Contents |
|---|---|
| `output/delivered/supporting/` | Current v27 pair and two-page market-sizing handback |
| `output/delivered/supporting/archive/` | Previous story versions, background, illustrations and history records |
| `output/delivered/archive/` | Earlier Convergence and workplan deliveries |
| `qa/` | Local renders, checks and unique unshipped review drafts |
| `story/` | Canonical copy, source evidence and illustration definitions |
| `scripts/` | Presentation-only builders; model calculations remain in `src/lfm/model/` |
| `templates/` | Original supplied presentation templates |

Model source-review reports have their own [delivery index](../output/delivered/README.md).
It links to the same presentation files and does not hold duplicate decks.

## Revisions and checking

v27 uses the supplied Vopak master and named layouts. Its sector-chart builder is
`scripts/build_sa_sector_charts_v27.ps1`, reading the archived v26. The preceding
workbook revision uses `scripts/prepare_sa_workbook_v26.py` and
`scripts/build_sa_workbook_v26.ps1`, reading archived v25. These are preserved
revision steps; choose a new version for further deliveries.

Build into QA, run package checks, export through PowerPoint and visually inspect.
Preserve delivered vintages and update the current manifest, hashes and delivery
index. Use `scripts/check_sa_revision.py` with the current rendered slide PNGs.
The [8 October cleanup record](output/delivered/supporting/archive/records/cleanup_2026-10-08_v27.json)
maps archived files and duplicate removals. Historical snapshots retain their original paths.

Observed data, estimates, proposed cases and investment illustrations remain separately
labelled. Sources, original templates, unique model outputs and prior deliveries are retained.
File consolidation does not imply input or business approval.
