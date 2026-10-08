"""Comparable historical series for the South Africa review; no source splicing."""
import pandas as pd


def complete_period_totals(frame, *, periods_per_year):
    """One series in; retain only distinct, complete months or quarters."""
    if periods_per_year not in (4, 12):
        raise ValueError('Expected quarterly or monthly data')
    data = frame[['period', 'value']].copy()
    data['period'] = data.period.astype(str)
    if data.period.duplicated().any():
        raise ValueError('Competing observations for a period; choose a source explicitly')
    data['year'] = data.period.str[:4].astype(int)
    output = {}
    for year, group in data.groupby('year'):
        expected = ({f'{year}-Q{q}' for q in range(1, 5)} if periods_per_year == 4
                    else {f'{year}-{m:02}' for m in range(1, 13)})
        if set(group.period) == expected and group.value.notna().all():
            output[int(year)] = float(group.value.sum())
    return output


def annual_series(frame, *, scale=1):
    if frame.period.duplicated().any():
        raise ValueError('Competing annual observations; do not silently average')
    if scale <= 0:
        raise ValueError('Scale must be positive')
    return {int(r.period): float(r.value) / scale for r in frame.itertuples() if pd.notna(r.value)}


def rebase(series, year):
    if year not in series or series[year] <= 0:
        raise ValueError('A positive observed base is required')
    return {y: v / series[year] * 100 for y, v in series.items()}


def endpoint_change(series, start, end):
    if end <= start or start not in series or end not in series or series[start] <= 0:
        raise ValueError('Comparable positive starting observation and later endpoint required')
    return (series[end] / series[start] - 1) * 100
