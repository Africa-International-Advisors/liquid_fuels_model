# Review pack figures checked against the inputs, 7 October 2026

Priority 5 on Manish's focus page. Pack checked:
`pptx/output/delivered/Vopak_Week1_Convergence_review_2026_10_07.pptx` (31
pages), pages 4 to 10: market baseline, drivers and refinery capacity.

    python -m lfm.scripts.check_pack_figures --vintage 2026

reads the data stored behind each chart and the figures quoted in the page
text, recomputes each from the registered inputs, and writes
`pack_figure_check_2026-10-07.csv`, one row per figure.

## Result

| Page | Figures checked | Match | Differ |
|---|---|---|---|
| 4 National balance, 2024 | 8 quoted | 8 | 0 |
| 5 Sales by province, 2022 | 15 quoted | 15 | 0 |
| 6 Provincial history 2013-2022 and 2024 petrol estimates | 90 chart points, 3 quoted | 93 | 0 |
| 8 Activity drivers | 38 chart points | 38 | 0 |
| 9 Power, vehicle mix, prices | 46 chart points | 46 | 0 |
| 10 Refinery capacity | 20 chart points to 2025, 4 quoted | 24 | 0 |
| **Total** | **224** | **224** | **0** |

A further 64 chart points on page 10 are the authored scenario (capacity held
flat to 2036 and the conditional 400 thousand barrels a day from 2033). They
are not observations and are marked "not checked".

No figure needs correcting. Page 7 uses the same provincial totals as page 5;
its domestic and import split is labelled illustrative and was not checked.
Page 11 has no figures.

## Points on labels and currency, for Nigel

| Page | Point | Suggested change |
|---|---|---|
| 4 | 2024 sales are FIASA's 2025 edition, labelled unverified. Since the pack was built, Road Accident Fund accounts show 24.4 bn litres of petrol and diesel levied in the year to March 2025 against 20.76 recorded, with volumes rising | Add the levy figure as a second bar or a note, as new evidence |
| 6 | The 2024 petrol estimates hold 2022 shares (GP 3.47, KZN 1.47, WC 1.41). A back-test of six methods since found that quarter 1 2023 shares do better (2.5 share points misallocated against 4.4 two years ahead) | If the new method is adopted: KZN 1.47 to 1.45 and WC 1.41 to 1.47; GP stays 3.47 |
| 6 | "Manish fixed the 2013 parser and traced 2015 to a revision" | Correct as written |
| 8 | Freight is payload in tonnes, not tonne-kilometres | Already implied by "payload"; no change |
| 9 | The plug-in hybrid index reaches 381 in 2025 on a 2024 base because 2024 sales were small (738 vehicles) | Consider showing vehicles sold instead of an index |
| 10 | Published capacity keeps Astron at 100 thousand barrels a day through 2020-2022. The Cape Town refinery was not operating for much of that period | Check, and say "published" capacity is not operating capacity for those years |
| 10 | Secunda's 150 is crude-equivalent capacity; the model input was 75 until today | Branch now carries 150 with utilisation re-based; decision D08 |

The Astron point is from memory of press reports, not from a source held in
the repository; it needs confirming before the page is changed.

## Not checked

- Pages 12 to 31, including the three lever pages (covered by the lever
  response) and the footprint, handling and inventory pages.
- Wording and layout.
