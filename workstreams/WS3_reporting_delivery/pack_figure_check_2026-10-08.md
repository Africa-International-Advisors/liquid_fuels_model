# Current pack figures checked against the inputs, 8 October 2026

Priority 5 on Manish's focus page. Pack checked:
`pptx/output/delivered/Vopak_Convergence_current.pptx` (30 pages, pushed to
`main` on the evening of 7 October). This replaces the check of the 31-page
review pack made earlier that day, which found the same result.

    python -m lfm.scripts.check_pack_figures --vintage 2026

reads the data stored behind every chart in the pack and the figures quoted in
the text of pages 4 and 5, recomputes each from the registered inputs, and
writes `pack_figure_check_2026-10-08.csv`, one row per figure. Chart series are
recognised by name, so the check can be re-run when pages move.

## Result

| Page | What it shows | Figures checked | Match | Differ |
|---|---|---|---|---|
| 4 | Petrol and diesel sales, imports, exports and net imports, 2019-2025 | 62 | 62 | 0 |
| 5 | Sales by province: 2022 map and 2013-2022 history | 82 | 82 | 0 |
| 6 | Refinery capacity by site, 2016-2025 | 60 | 60 | 0 |
| 16 | Activity drivers | 38 | 38 | 0 |
| 17 | Power, vehicle mix and prices | 46 | 46 | 0 |
| **Total** | | **288** | **288** | **0** |

Not checked, because they are not observations: 87 points on page 6 (capacity
held flat from 2026 and the conditional addition) and 4 points on page 24 (the
illustrative inventory sensitivity).

No figure needs correcting. The page 4 title (net imports up 15% for diesel
and 19% for petrol in 2025) is right: 15.1% and 18.5%.

## Points on labels and currency, for Nigel

| Page | Point | Suggested change |
|---|---|---|
| 4 | FIASA's 2024 sales are shown as an unresolved point. Road Accident Fund accounts, found on 7 October, give 24.4 bn litres of petrol and diesel levied in the year to March 2025 against 20.76 recorded, with volumes rising | Add as a note; it is the only independent count found |
| 4 | "Comparable national petrol/diesel production is not yet available" | Correct. The energy balances give production by product to 2021; the workbook's History sheet shows it |
| 5 | 2014 and 2018 are withheld from the provincial trend | Agrees with the open decision (D05). The workbook shows both years with the difference from the national file |
| 5 | No 2023-2025 provincial figures are shown | A tested estimate now exists (quarter 1 2023 shares); it is on the workbook's History sheet, section 6, if wanted |
| 6 | Published capacity keeps Astron at 100 thousand barrels a day through 2020-2022, when the Cape Town refinery was, as far as I recall, largely not operating | Check against a source, and label the chart as published capacity, not operating capacity |
| 6 | Sasol is shown at 150 | Matches FIASA. The model input was 75 until 7 October; the branch now carries 150 with utilisation re-based (decision D08) |
| 17 | The plug-in hybrid index reaches 381 in 2025 on a 2024 base, because 2024 sales were 738 vehicles | Consider showing vehicles sold |

The Astron point is from memory of press reports, not from a source held in
the repository.

## Not checked

- Pages 7 to 15 and 18 to 30: logistics tests, roadmap, scenario framework,
  the three lever pages (covered by the lever response) and the appendix
  text. None of these carries a chart of observations.
- Wording and layout.
