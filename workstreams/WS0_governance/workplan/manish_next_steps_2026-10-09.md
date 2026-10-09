# Manish: next steps from the market sizing pack, 9 October 2026

For Manish, from Nigel. The pack built on your DR01, DR04, DR07 and DR08 hand-back
(PR #1) is `pptx/output/delivered/supporting/09102026_Vopak_Market_Sizing_v1100.pdf`
(cover plus eight pages). Page 8 lists decisions and next steps; this note expands the
items that are yours, with what "done" looks like. No delivery dates are committed here.

## How the pack uses your files

The pack does not hold its own numbers. `pptx/scripts/issue_tree_volumes.py` reads your
registered files and writes `pptx/story/issue_tree_volumes_2026_10_08.json`; the builder
reads that file. When you update an input, rebuild:

```powershell
python pptx/scripts/issue_tree_volumes.py
pptx/scripts/build_market_sizing_issue_tree.ps1 -IncludeRequests -Layout flow
```

Files read: `fuel_balance_petrol_diesel_2009_2025_2026-10-06.csv`,
`provincial_petrol_diesel_2013_2024_2026-10-06.csv`, `provincial_share_backtest_2026-10-08.csv`,
`sector_baselines_2026-10-07.csv`, `dr07_demand_evidence_2026-10-08.csv`,
`fuel_lever_response_2026-10-07.csv`, and the registered `fuel_trade_sars_by_office.csv`,
`port_liquid_bulk_tnpa.csv`, `energy_balance_department.csv`, `fuel_sales_department_by_province.csv`.
Page 6 text is in `pptx/story/logistics_evidence_2026_10_08.json`. Outputs are named
`ddmmyyyy_filename_vHHMM` (build time to the nearest half hour).

Where our work overlapped, your evidence is primary:
`workstreams/WS0_governance/workplan/overlap_log_2026_10_08.md`. Item 1 there records that
my earlier page showed a residual as production; it is withdrawn.

## Yours to execute, in priority order

| # | Task | Pack page | Done when |
|---|---|---|---|
| 1 | **Market sizing method for Durban and Lesedi.** Estimate the accessible annual market for each site by product, from destination demand (provincial file), entry points (customs by office), feasible routes (trunk-line capacity, Lesedi intake, road), and competing supply. | 2 (Vopak column), 3, 6 | Ranges by site and product with explicit denominators; shared Durban-Lesedi flows counted once; every input labelled observed, estimated or assumed; no client data assumed. |
| 2 | **Demand-by-use calibration** with Nigel. Explain the power gap (model 3.6B L against 0.9-1.6B L reported) and what sits in the balance's 5.3B L "other". Propose one baseline. | 4 | A short note: proposed values by sector, the reconciliation to sales, and what changes in the model; agreed with Nigel before any input changes. |
| 3 | **DR07 double-count check.** Road activity vs rail diversion; battery EV share vs new-vehicle efficiency; hybrids vs efficiency. | 5 | For each pair, how the levers combine in the engine and whether any case counts the same saving twice; a test where possible. |
| 4 | **Figure check for this pack.** Extend `lfm.scripts.check_pack_figures` (or a sibling) to re-compute the volume and evidence JSON files from the registered inputs. | all | A check that fails if any number on the pack differs from its input; result written beside your Convergence check. |
| 5 | **DR04 open lines.** Petrol and diesel volumes on the trunk line; NERSA reasons for decision and tariffs beyond Durban-Alrode; zone differentials after April 2024; the 10-11 c/l gap between tariff and regulated differential; matched delivered cost to the same destination. | 6 | Each line closed with source and page, or marked not available with where you looked. |
| 6 | **Trunk-line capacity today.** Your lead: 148M L a week (2020) is about 7.7B L a year against 13.2B L landed at Durban in 2025. Find a current capacity statement. | 6 | A dated capacity figure with source, or confirmation that none is published (then Nigel asks Transnet). |
| 7 | **DR01 open line.** Why the 2021 energy balance imports (diesel 11.2B L) exceed customs (9.8B L). | 1 | Explanation from the department's working, or recorded as unexplained. |

## Nigel coordinates (for awareness)

- Client requests DR02/05, DR03, DR06 (prepared, not sent): site throughput, tanks, economics.
- Operator data: Secunda and Astron output by product; stock change by product (DR08, DR01).
- Whether Vopak Durban can inject into the NMPP (DR04).
- Recording receipt of DR01, DR04, DR07, DR08 in `output/delivered/investment_bridge_2026_10_08/data_request.csv`.
- Decisions on page 8: demand-by-use baseline, lever cases (with Henry), coastal/inland grouping.

## Keep

- The TNPA all-liquids port tonnage stays tracked and shown beside fuel-only customs litres (page 6).
- FIASA and JODI stay excluded as sources.
- Nothing is accepted until Nigel signs off; open exceptions mean outputs are provisional.
