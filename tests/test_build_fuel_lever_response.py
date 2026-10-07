"""The lever response keeps Nigel's proposed values intact and matches a fresh build."""
import csv
from pathlib import Path

from lfm.scripts import build_fuel_lever_response as resp

ROOT = Path(__file__).resolve().parents[1]
VINTAGE = ROOT / "assumptions" / "2026"


def _read(path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_response_covers_every_proposed_value_without_altering_it():
    proposed = _read(VINTAGE / "timeseries" / resp.PROPOSED)
    rows = resp.build(proposed, resp.review(resp.baselines(VINTAGE / "timeseries", VINTAGE / "reference")))
    assert len(rows) == len(proposed) == 120
    for given, row in zip(proposed, rows):
        assert (row["fuel"], row["lever"], row["period"], row["case"]) == (
            given["fuel"], given["lever"], given["period"], given["case"])
        assert row["proposed_by_nigel"] == given["value"]
        assert (row["changed"] == "yes") == (float(row["analyst_value"]) != float(given["value"]))
        assert row["baseline"] and row["baseline_basis"] and row["evidence"]


def test_replacements_keep_low_medium_high_in_order():
    proposed = _read(VINTAGE / "timeseries" / resp.PROPOSED)
    rows = resp.build(proposed, resp.review(resp.baselines(VINTAGE / "timeseries", VINTAGE / "reference")))
    by_lever = {}
    for row in rows:
        by_lever.setdefault((row["fuel"], row["lever"], row["period"]), {})[row["case"]] = float(row["analyst_value"])
    for key, cases in by_lever.items():
        assert cases["low"] <= cases["medium"] <= cases["high"], key


def test_committed_response_matches_a_fresh_build():
    proposed = _read(VINTAGE / "timeseries" / resp.PROPOSED)
    rows = resp.build(proposed, resp.review(resp.baselines(VINTAGE / "timeseries", VINTAGE / "reference")))
    assert _read(ROOT / resp.OUT_DIR / f"{resp.STEM}.csv") == rows
