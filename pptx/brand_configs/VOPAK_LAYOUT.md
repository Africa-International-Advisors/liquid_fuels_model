# Approved Vopak exhibit layout

Approved 12 October 2026. Source: slide 7 of Vopak_Convergence_current.pptx,
preserved in templates/Vopak_Approved_Exhibit_Reference_v1.pptx. Its SHA-256
is pinned in vopak_layout.json. The reference deck is retained intact so its
original master, layout relationships and native shapes remain recoverable.

## Ownership

brand-pptx supplies generic presentation capabilities. This project owns Vopak's
reference, layout contract and extension. They are persistent repository source;
they do not live in an installed package cache or depend on chat memory.
No package source has been copied or patched. The existing kickoff build remains
separate from the South Africa evidence-deck delivery workflow.

## Standard

- Named layout: **Vopak Exhibit + Commentary v1**, registered under the existing
  supplied master by the extension.
- Lato, native black panel headings and thin horizontal rules.
- Exact reference panel geometry and native circle with two white arrow segments.
- Navigation: 1 Overview / 2 Market baseline / 3 Market changes / 4 Vopak outlook.
- Charts and maps stay left; implications stay right. Tables and issue trees
  retain their approved bodies and receive the common navigation.
- Cover and closing retain their approved designs.

## Current evidence-deck build

Run from repository root, with the shared environment:

```powershell
.venv/Scripts/python.exe pptx/scripts/lock_vopak_layout.py INPUT.pptx NEW_OUTPUT.pptx
.venv/Scripts/python.exe pptx/scripts/lock_vopak_layout.py NEW_OUTPUT.pptx --check
```

The current adapter targets the 14-page evidence pack: exhibits 4â€“10,
navigation 2â€“13. For a different deck, explicitly map its roles and content
into this contract; do not assume the same slide numbers or shape names.
Do not rerun legacy builders directly into delivered/. Apply this layout stage
after the content builder, before package finalization and PDF export.

The extension copies approved native components, preserves all chart/workbook
parts byte-for-byte, checks headings/rules/divider geometry and navigation, and
refuses to overwrite an output. Finalize with the presentation package checker,
render in PowerPoint, inspect all affected pages, and verify p3 hyperlinks.

## Acceptance

The XML check catches layout drift, but does not prove readable text or correct
analytics. Render review remains required. Update both the reference and contract
only after explicit user approval; preserve prior versions.

For the 16-page v08 pack, run the layout check with `--profile evidence_v08`. The named-layout and geometry checks cover pp4–11 and p14; navigation covers pp2–15. v08 adds pages by duplicating the locked v07 layout.

## Accepted v10 and repository cleanup

The current deck is `pptx/output/delivered/supporting/SA_SCR_Evidence_2026-10-12_v10.pptx`. Run `--check --profile evidence_v09` against it: that profile includes the p2 balance chart and all subsequent evidence exhibits. V10 changes only the p4 chart type to stacked area. Older SCR vintages are under `supporting/archive/2026-10-12_accepted_v10/`; builder inputs were repointed. Source chart snapshots are saved in `pptx/story/`, so the v06/v08/v09 chart builders do not require ignored QA data. Generic runtime tools remain external prerequisites.
