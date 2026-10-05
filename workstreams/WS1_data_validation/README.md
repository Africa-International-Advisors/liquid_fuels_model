# WS1 ? Data and validation

Proposed delivery owner: analyst (name pending). Accountable lead: Nigel.

Source and reconcile opening fleet, mileage, fuel consumption, sales mix, retirement,
sector baselines, aviation/generation drivers and refinery data. Start regional data requests
early. Define sector/product boundaries to avoid double counting.

Outputs: source coverage map, updated assumption register, historical reconciliation and
explanations for material gaps. Keep received files in `external/`, curated inputs in
`assumptions/`, audit rows in `governance/` and calculated comparisons in `runs/`.

Acceptance: sources and definitions reviewed; reconciliation thresholds agreed; unsupported
inputs remain explicit exceptions. Matching a total does not by itself validate the inputs.

## Source audit

Run `.venv\Scripts\python.exe -m lfm.scripts.audit_source_inputs --vintage 2026`.
The audit runs both defined scenarios and exports flags for every declared input,
all CSV files, original-source evidence, duplicate dimensions and provincial coverage.
It records engine requests after snapshot preloading. A requested block does not prove
that every row or country slot influences the output, and a matching document hash
does not independently verify its figures. Results are preserved in a new `runs/` folder.

The 5 October review found no recorded independent verification for 28,122 declared
inputs. Review used provisional parameters first, then incomplete provincial totals,
repeated historical/refinery keys, missing originals and unreadable source metadata.
See `output/delivered/Liquid_fuels_source_audit_2026_10_05.xlsx` for the investigation
list and exact file locations. Existing open exceptions remain in force; this audit
does not change assumptions or record approval.

## Source profile and key URL tests

Run `.venv\Scripts\python.exe -m lfm.scripts.profile_data_sources --audit <audit-folder>/audit.json`.
This profiles declared blocks plus undeclared CSVs as time series, dated snapshots,
scalars, structured parameters or reference tables. It records units, time coverage,
refresh route and the model-access trace from the audit. Scalars inside structured
country/scenario blocks remain grouped; six standalone scalar blocks are not the
total number of scalar values.

The live connectivity check samples key publisher pages, API responses and document
URLs. It retries a failed sample once, retaining the initial failure. This is neither
a test of all historical URLs nor proof of a full download, parser completeness,
freshness or source accuracy. Runs are on demand; no background service is scheduled.
Use `--prior-pass <profile.json>` to retain failures from an earlier pass.
The delivered HTML profile and connectivity CSV are under `output/delivered/`.
