# DR07 Demand evidence, 8 October 2026

For Nigel's review. Answers request DR07: the evidence that calibrates the
demand levers. Petrol and diesel only.

Status: **15 facts read from sources, 5 calculated, 8 not available.**

**Where to look:** the workbook `output/delivered/Demand_baseline_workshop_2026_10_08_history.xlsx`.

- Sheet **DR07 evidence**: every fact with its source and open gap.
- Sheet **DR07 power diesel**: Eskom's reported litres beside its generation.
- Sheet **DR07 fleet by province**: registered vehicles by province and class.

Table behind the first sheet: `dr07_demand_evidence_2026-10-08.csv`, rebuilt by
`python -m lfm.scripts.build_dr07_demand_evidence --vintage 2026`.

## Reported Eskom diesel litres

Eskom reports the fuel burned at its turbines. Years to 31 March:

| Year to March | Eskom fuel burned, bn litres | Eskom generation, GWh | Litres per kWh | Independent plants, GWh | Independent plants, bn litres (estimated) | Total, bn litres |
|---|---|---|---|---|---|---|
| 2023 | 0.94 | 3,018 | 0.311 | 1,098 | 0.34 | 1.28 |
| 2024 | 1.13 | 3,634 | 0.311 | 1,509 | 0.47 | 1.60 |
| 2025 | 0.68 | 2,176 | 0.312 | 662 | 0.21 | 0.88 |

Source: Eskom Integrated Report 2025, PDF p.141, checked against the page.
The sheet has all ten years, 2016 to 2025. Two points:

- Reported litres over reported generation gives 0.311 to 0.312 litres per
  kWh, which confirms the 0.31 used on the Power fleet sheet.
- Eskom reports diesel and kerosene together. Two of its four stations burn
  kerosene, but they are 342 of 2,426 MW, so nearly all of it is diesel.

The independent plants (Avon and Dedisa) do not report litres; theirs are
estimated from generation at Eskom's rate.

## Not available

| What | Why it matters |
|---|---|
| Diesel burned in private backup generators | No source measures it. It is inside recorded diesel sales and cannot be separated. |
| New gas or diesel plant: commissioning dates | The Integrated Resource Plan gives totals, not plant dates. Needed to place diesel backup at new gas plant. |
| Vehicles by fuel within each class, and by province | Needed to say how many diesel bakkies or petrol cars each province has. eNaTIS publishes class and province, not fuel. |
| Vehicles by age | Needed for fleet replacement. Only apparent retirements can be calculated (Vehicle history sheet). |
| Electric trucks and electric light commercial vehicles sold | naamsa does not report electric sales by segment. Benchmarks from other countries are on the HML response sheet. |
| Efficiency of new vehicles, by year | No annual series of new-vehicle fuel use was found, so there is no efficiency history. |
| Road freight in tonne-kilometres, by year | Needed to size freight that could move to rail. Only single-year figures exist in published studies. |
| Diesel used by rail locomotives | Needed so that freight moving to rail is not counted as diesel saved in full. |

## Checks

- The evidence table is rebuilt from registered inputs, and a test checks the
  committed file equals a fresh build and that every fact has a source.
- Eskom's ten fuel figures were read against the report page.
- The provinces on the fleet sheet add to the national register (tested).
- FIASA and JODI are not used.
- No model input changed; model results are unchanged.
