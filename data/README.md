# Raw historical data

Local-only working copy of source data (SAPIA volumes, IEA stats, Stats SA
GDP series, NamPower / NPC dispatch, etc.). Subdirectories `raw/` and
`interim/` are gitignored — these files are not part of the vintage.

What *is* part of the vintage lives under `assumptions/<vintage>/timeseries/`
as cleaned, schema-conformant CSVs. The flow is:

```
data/raw/  →  notebook / ETL  →  assumptions/<vintage>/timeseries/*.csv
```

Treat this directory as a scratchpad; the vintaged outputs are the
contract with the model.
