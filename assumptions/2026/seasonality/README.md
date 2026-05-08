# Seasonality indices

CSVs in this directory hold per-country×segment monthly seasonality indices,
referenced by name from the segment YAMLs (e.g. `aviation_za`, `industrial_bw`).

Schema for each CSV:

```
month,index
1,0.92
2,0.88
...
12,1.18
```

The 12 monthly indices should average to 1.0 (otherwise they shift the
annual total, which the held-segment growth path is supposed to set
independently).

These are *fitted from history* — when the team refreshes a vintage,
re-fit using the latest available monthly observations for that
country×segment and replace the file.
