# Market sizing for Durban and Lesedi, 9 October 2026

For Nigel's review. Task 1 of `manish_next_steps_2026-10-09.md`: the accessible market
for each Vopak site, from public data only. No client data is assumed.

Table: `market_sizing_durban_lesedi_2026-10-09.csv`, rebuilt by
`python -m lfm.scripts.build_market_sizing --vintage 2026`. The pack's framework page
(page 2, Vopak column) reads it through `pptx/scripts/issue_tree_volumes.py`.

## The answer in one table

Billion litres a year, petrol and diesel together.

| | Low | High | What each end is |
|---|---|---|---|
| Durban | 4.3 | 13.2 | KwaZulu-Natal sales (2022), to everything landed at Durban (2025) |
| Lesedi | 6.8 | 12.0 | Gauteng sales (2022), to sales in all six inland provinces (2022) |
| Both sites, counted once | | 13.2 | Everything landed at Durban |

Between the two: about **8.9 billion litres** of the fuel landed at Durban moves inland.
That is the flow Lesedi competes for, and it is already inside Durban's 13.2.

## By product

| Billion litres a year | Petrol | Diesel | Both |
|---|---|---|---|
| Landed at Durban, 2025 | 4.23 | 8.93 | 13.16 |
| Coastal catchment: KwaZulu-Natal sales, 2022 | 1.50 | 2.79 | 4.28 |
| Inland-bound through Durban | 2.73 | 6.15 | 8.88 |
| Gauteng sales, 2022 | 3.53 | 3.28 | 6.81 |
| Six inland provinces' sales, 2022 | 5.55 | 6.40 | 11.95 |

## Method

1. **Durban, high:** imports cleared at the Durban customs office. Observed. It is 79% of
   all petrol and diesel imported, and the most any Durban terminal can handle.
2. **Durban, low:** KwaZulu-Natal sales. Observed. It assumes the province is supplied
   from Durban, since both Durban refineries have stopped refining (DR08).
3. **Inland-bound:** landed at Durban less KwaZulu-Natal sales. Estimated: it mixes
   2025 imports with 2022 sales and ignores coastwise shipments.
4. **Lesedi, low and high:** Gauteng sales and the six inland provinces' sales. Observed.
   Part of both is supplied by Natref and Secunda, whose output by product is not
   published after 2021, so these are catchments, not import needs.
5. **Counted once:** every litre Lesedi receives by pipeline landed at Durban first, so
   the two site markets are never added together.

## Against the route and the tanks

- **The trunk line cannot carry all of it.** Its stated capacity is 7.7 billion litres a
  year (Transnet, 2020, all products including jet). The inland-bound flow is 8.9, so at
  least 1.2 billion litres a year leaves Durban by road or rail.
- **What the tanks allow.** At two turns a month, Durban's tanks allow about 3.5 billion
  litres a year and Lesedi's about 3.0. These are ceilings, not shares: the turns are
  analyst estimates from `terminal_site_assumptions.csv`, and actual throughput needs
  the client (DR02/05).

| Site | Tanks, operational | 1 turn a month | 2 turns | 3 turns (Lesedi 2.4) |
|---|---|---|---|---|
| Durban | 146,000 m3 (estimated) | 1.75 | 3.50 | 5.26 |
| Lesedi | 124,000 m3 | 1.49 | 2.98 | 3.57 |

## What this does not settle

- **Market share and headroom** stay pending. They need each site's actual throughput.
- **The inland gap.** Inland sales of 12.0 less 8.9 arriving through Durban leaves about
  3 billion litres to come from Natref, Secunda and Matola. Their reported output looks
  larger than that, so the figures do not yet close. This is the "3 billion litre
  question" from the call of 9 October and it cannot be tested without production data.
- **Years.** Imports are 2025 and provincial sales are 2022, the last year published by
  province.
- **Competing terminals.** Ten operators hold leases at Island View, and Transnet's own
  storage sits beside Lesedi at Jameson Park. The site markets are what is there to
  compete for, not what Vopak can win.

## Checks

- A test rebuilds the table from the registered inputs and compares it with the file.
- Petrol and diesel add to the totals; the combined line equals Durban's landed volume.
- Every row is marked observed, estimated or assumed and names its inputs.
