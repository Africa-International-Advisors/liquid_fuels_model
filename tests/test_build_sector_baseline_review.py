"""The sector baseline review: committed file matches the engine, and only two segments move."""
import csv
from pathlib import Path

from lfm.scripts import build_sector_baseline_review as review

ROOT = Path(__file__).resolve().parents[1]


def test_committed_file_matches_the_engine_and_only_agriculture_and_industry_change():
    with (ROOT / review.OUT).open(encoding="utf-8", newline="") as fh:
        committed = [r for r in csv.DictReader(fh) if r["scenario"] == "high_demand"]
    fresh = [{k: str(v) for k, v in row.items()} for row in review.build_rows("2026", ("high_demand",))]
    assert committed == fresh, "rebuild with: python -m lfm.scripts.build_sector_baseline_review --vintage 2026"

    moved = {r["segment"] for r in fresh if int(r["difference"]) != 0}
    assert moved == {"agriculture", "industrial"}
    effect_2024 = sum(int(r["difference"]) for r in fresh if r["period"] == "2024") / 1e9
    assert round(effect_2024, 2) == -0.63
