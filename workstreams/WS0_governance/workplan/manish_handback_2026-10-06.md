# Hand-back to Nigel, 6 October 2026

Reply to `manish_handover_2026-10-06.md`. All work is on `manish-branch`, up to
commit `1416197`. Nothing has gone to `main`.

Update deck: `pptx/output/delivered/Vopak_Manish_Handback_2026_10_06.pptx` (PDF
alongside). It covers the five packages, the lever sheet and the decisions
below. It was built before the provincial GDP and 2015 items were closed, so
it does not mention them.

## Where things stand

- **Integrity:** the 2013 national sales figure was our parsing error and is
  corrected. The refinery repeats came from an over-long named range and are
  fixed. The 2015 province-versus-national difference is a revision between
  two department files.
- **Traceability:** the source trace covers 46 datasets. Six are used by the
  engine, all from the Reatile workbook.
- **Provincial petrol and diesel:** the department has published nothing by
  province after 2023-Q1. The estimate holds 2022 shares against national
  sales. Stats SA provincial GDP to 2024 is in the inputs and shows shares of
  activity barely moving.
- **Fuel balance:** SARS customs data is the primary trade source from 2014,
  with FIASA kept as a cross-check and for earlier years. The diesel gap of 3
  to 4 bn litres a year is supported by several sources.
- **Driver evidence:** Stats SA monthly activity and fuel prices to October
  2026 are in the inputs and the one-command refresh. Coastal diesel has no
  value from December 2025 because the department stopped publishing it.
- **Levers:** draft sheet at
  `workstreams/WS2_model_development/lever_sheet_2026-10-06.md`.

## Decisions left for Nigel

- Treatment of the 2014 and 2018 provincial differences.
- The marine baseline, the elasticities and the road parameters.
- Which national sales series to use for 2024, and the related balance items.
- Committing the remaining original files.

## Checks

- `python -m pytest -q`: 156 passed, 1 skipped.
- `python -m lfm check --vintage 2026`: coverage passed, 52 open exceptions,
  so output remains draft.

## Where the evidence is

`workstreams/WS1_data_validation/`: `integrity_flag_log_2026-10-06.md`,
`source_trace_2026-10-06.csv`, `provincial_demand_after_2022_2026-10-06.md`,
`fuel_balance_2026-10-06.md`, `driver_evidence_2026-10-06.md`.
