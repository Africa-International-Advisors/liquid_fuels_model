# Run outputs

Each model execution writes its xlsx (and any auxiliary parquet/CSV)
into a subdirectory tagged with the Run identifier:

```
runs/<vintage>-<scenario>-v<model_version>/
    output.xlsx
    demand_long.parquet
    flows_long.parquet
    provenance.json
```

This directory is gitignored. Outputs are *generated*, not committed —
reproducibility comes from the (vintage, scenario, model_version) triple
plus the immutable assumption vintage, not from versioning the artifact.
