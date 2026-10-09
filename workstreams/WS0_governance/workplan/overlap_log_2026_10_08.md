# Overlap log: issue-tree pack and Manish's DR01-DR08 hand-back, 8 October 2026

On 8 October the issue-tree pack (v3-v9, built by Nigel with Claude) and Manish's
DR01, DR04, DR07 and DR08 evidence (merged to `main` as PR #1, 2745cd8) covered some
of the same ground in parallel. This log records each overlap, which version is
primary from v10 onward, where the figures differ, and what remains open. Nothing
here is a finding about either piece of work being wrong unless stated.

Rule from v10: where both exist, Manish's registered evidence is the source for the
pack, because it is reconciled, tested and registered. Pack-only material is kept
only where his evidence has no equivalent, and is labelled as such.

| # | Topic | Pack version (Nigel/Claude) | Manish version | Primary from v10 | Differences | Action |
|---|---|---|---|---|---|---|
| 1 | National petrol and diesel balance | `pptx/scripts/issue_tree_volumes.py` computed its own balance; v9 page 1 showed 2023-24 production as sales less net imports | DR01; `workstreams/WS1_data_validation/fuel_balance_petrol_diesel_2009_2025_2026-10-06.csv`, built by `lfm.scripts.build_fuel_balance` | Manish | v9 labelled a residual as production (fails the DR01 acceptance test). v9 used energy-balance trade for 2021 (imports 16.6B L) where DR01 uses customs (13.8B L). v9 used balance final consumption for 2021 (23.2B L) where DR01 uses department sales (22.3B L) | v10 page 1 reads the DR01 file; the pack's own balance calculation is retired; implied production withdrawn |
| 2 | Trade source | Department trade review, rounded narrative (2023 imports 17.3B L, exports 1.94B L; 2024 imports 14.8B L) | SARS customs, `fuel_trade_sars.csv` (2023 imports 17.35B L, exports 1.88B L; 2024 imports 14.79B L) | Manish | Rounding only; exports differ by 0.06B L in 2023 | v10 uses customs throughout |
| 3 | 2024 sales | FIASA 20.8B L shown on v9 page 1 as "unverified" | DR01 excludes FIASA (instruction of 7 and 8 October); two FIASA editions disagree for 2024 | Manish | v9 used an excluded source | 2024 row removed; the PS "~20B" stays as quoted text only |
| 4 | Port and logistics evidence | Public-source research on 8 October: `pptx/story/logistics_evidence_2026_10_08.json`, PDFs in `external/sources/logistics_2026_10_08/` | DR04; `dr04_routes_access_evidence_2026-10-08.csv`, originals in `external/data/raw/routes_access_20261008/` | Manish, with pack additions labelled | Same pipeline capacity (148M L a week, Transnet Pipelines 2020). v9 used TNPA all-liquid-bulk tonnage; DR04 excludes it as "other products included" and uses customs entry points (petrol and diesel only). Four PDFs were downloaded twice (byte-identical): Transnet IR 2025, NERSA 2025-27 tariff statement, TNPA report 2024, Transnet Pipelines 2020. Pack-only items: Transnet Pipelines 2024 utilisation (97 of 148M L a week), FY25 total volume 13.4B L, NERSA jet fuel paper (rail-to-pipeline shift), Transnet IR 2025 road-loss risk | Duplicate PDFs removed from the pack folder and its README points to Manish's copies; pack-only items marked "pack research" on page 3 |
| 5 | Coastal and inland demand | Province proxy, 2022 department provincial sales (coastal = KZN, WC, EC) | `provincial_petrol_diesel_2013_2024_2026-10-06.csv` and back-test | Same underlying data | No difference for 2022. Manish adds a 2023 provincial estimate (back-test error 2.5 points petrol, 5.3 diesel). The coastal/inland grouping is pack-only and unregistered | Keep 2022 observed; grouping flagged as a presentation proxy needing a register row if adopted |
| 6 | Demand by use | 2021 energy balance final consumption: road 15.1, industry 1.6, agriculture 1.2, other 5.3B L | `sector_baselines_2026-10-07.csv` (model, 2024, high demand): vehicles 16.4, industrial 1.5, agriculture 1.06, generation diesel 3.58, marine diesel 0.77B L | **Not reconciled** | Different year, basis and sector grouping. The model's 3.58B L generation diesel is far above Eskom's reported 0.68-1.13B L (DR07) | Open: Nigel and Manish to agree which baseline the issue tree shows. v10 keeps the balance split, labelled as such |
| 7 | Refinery status and output | v9 notes cite closures generally | DR08: six plants, operating capacity 358,000 bbl/d; no product output after 2021 on the department's basis | Manish | None in conflict | v10 cites DR08 |
| 8 | Figure checking | Builder checks fit and bounds only | `lfm.scripts.check_pack_figures` re-computes chart data for the Convergence pack | Manish's method | The issue-tree pack is text, not chart data, so his check does not cover it | Open: extend the check to the issue-tree volume and evidence files |

## Demand deep dives added in v12 (pages 3-5)

Built from Manish's files only, read through `pptx/scripts/issue_tree_volumes.py`; no
new analysis. They overlap in subject with pages of the v27 story pack, which remain the
fuller treatment:

| Pack page | Reads | v27 story pages on the same subject |
|---|---|---|
| 3 Demand by product and province | `provincial_petrol_diesel_2013_2024_2026-10-06.csv`, `provincial_share_backtest_2026-10-08.csv` | 29 (Gauteng scale); Convergence pack p.5 (2022 provincial map) |
| 4 Demand by use | energy balance 2021; `sector_baselines_2026-10-07.csv`; DR07 power rows | 7, 22 |
| 5 Demand parameters | `fuel_lever_response_2026-10-07.csv` (2035 cases) | 11, 12, 24, 27, 31, 32 |

Page 4 shows the three demand-by-use sources side by side for calibration (item 6 stays
open by decision of 9 October: "show all, we will calibrate"). Page 5 shows Manish's
proposed 2035 values, none accepted.

## Correction to the pack research

The pack research of 8 October reported TNPA liquid-bulk revenue as R3,347.2m (FY23/24)
and R3,319.3m (FY22/23). Those are **container** revenue, the row above liquid bulk in
the salient-features table (TNPA Integrated Report 2023/24, PDF p.10). Liquid-bulk revenue
is R1,033.6m and R878.4m, as in Manish's DR04 evidence. The wrong figure was never placed
in the pack.

## Port liquid bulk: tracked, not used for fuel sizing

The all-liquids port series is kept, by Manish, in two forms:

- **Registered monthly and annual tonnage**, `assumptions/2026/timeseries/port_liquid_bulk_tnpa.csv`,
  with register rows: landed, shipped, coastwise and transhipped, by port, calendar 2024-2025
  and monthly for Durban from July 2024 (January 2025 missing at source).
- **Annual KPI and revenue** in the DR04 evidence file: TNPA integrated reports, all ports,
  41.9, 41.8, 38.1, 35.5 and 38.9 million kilolitres (years to March 2020-2024; the reports print
  "million kilometres"), FY25 target 34.6; liquid-bulk revenue R750m, R878m and R1,034m
  (FY22-FY24).

These include crude, gas and chemicals and are in tons or a misprinted unit, so the pack
sizes the fuel market from customs litres instead. The tonnage stays useful as a trend
and port-share indicator: Durban landed 66% of all liquids by weight in 2024-25 against
79% of petrol and diesel imports by litres.

## Still open after v10

- Item 6: one demand-by-use baseline for the issue tree.
- Item 8: independent figure check for the issue-tree pack.
- The request register `output/delivered/investment_bridge_2026_10_08/data_request.csv` still shows DR01, DR04, DR07 and DR08 as "Prepared; not sent". It is a delivered record, so v10 states the received status on page 4 rather than editing it; the register owner should record receipt.
