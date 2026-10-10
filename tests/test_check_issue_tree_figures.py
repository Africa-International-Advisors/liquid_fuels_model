"""The market sizing pack's figures are recomputed from the registered inputs and must all match."""
from pathlib import Path

from lfm.scripts import check_issue_tree_figures as check

ROOT = Path(__file__).resolve().parents[1]


def test_every_headline_figure_on_the_pack_matches_its_input():
    rows = check.check(ROOT / "assumptions" / "2026")
    assert len(rows) >= 24
    assert [r["item"] for r in rows if r["result"] != "matches"] == []
    by_item = {r["item"]: r for r in rows}
    assert by_item["Imports through Durban, 2025"]["pack_value"] == 13.2
    assert float(by_item["Both Vopak sites, counted once"]["recomputed"]) == float(by_item["Durban market, high"]["recomputed"])


def test_a_changed_figure_is_reported_as_different(monkeypatch, tmp_path):
    import json

    volumes = json.loads((ROOT / check.VOLUMES).read_text(encoding="utf-8"))
    volumes["entry_points"]["durban"] = 14.0
    changed = tmp_path / "volumes.json"
    changed.write_text(json.dumps(volumes), encoding="utf-8")
    monkeypatch.setattr(check, "VOLUMES", changed)
    wrong = [r["item"] for r in check.check(ROOT / "assumptions" / "2026") if r["result"] != "matches"]
    assert wrong == ["Imports through Durban, 2025"]
