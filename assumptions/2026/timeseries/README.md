# Long time series

CSVs referenced by the YAMLs via the `csv:` field. Long-format,
one row per (country, period), schema:

```
country,period,value
ZAF,2024,...
ZAF,2025,...
BWA,2024,...
```

`period` is a year (annual driver) or `YYYY-MM` (monthly).
`country` is ISO3 (`ZAF`, `BWA`, `LSO`, `NAM`, `SWZ`) or `SACU` for
shared-across-countries series.

Files are part of the vintage and become immutable when the vintage
ships. To correct a number, open a new vintage rather than editing
a shipped file.
