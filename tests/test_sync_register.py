"""Register reconciliation touches only the named blocks and never marks anything reviewed."""

from lfm.scripts.sync_register import row_id, sync


def _input(assumption: str, block: str, value: str) -> dict:
    return {"assumption": assumption, "block": block, "value": value, "unit": "litres",
            "source": "s", "source_date": "2026-10-06", "owner": "o", "confidence": "unassessed",
            "register_group": "REG-X", "exception_id": "EXC-X"}


def _row(assumption: str, value: str, status: str = "unreviewed", reviewer: str = "") -> dict:
    return {"id": row_id(assumption), "assumption": assumption, "register_group": "REG-X",
            "value": value, "unit": "litres", "source": "s", "source_date": "2026-10-06",
            "owner": "o", "reviewer": reviewer, "review_status": status,
            "confidence": "unassessed", "validity": "2026", "exception_id": "EXC-X"}


def test_sync_keeps_updates_adds_and_removes_within_the_block_only() -> None:
    rows = [
        _row("a.x.same", "1", status="verified", reviewer="nigel"),
        _row("a.x.changed", "2", status="verified", reviewer="nigel"),
        _row("a.x.gone", "3"),
        _row("b.y.other", "9", status="verified", reviewer="nigel"),
    ]
    inputs = [
        _input("a.x.same", "a.x", "1"),
        _input("a.x.changed", "a.x", "20"),
        _input("a.x.new", "a.x", "4"),
        _input("b.y.other", "b.y", "999"),      # differs, but its block was not named
    ]
    out, counts = sync(rows, inputs, {"a.x"}, "2026")
    assert counts == {"kept": 1, "updated": 1, "added": 1, "removed": 1}
    by = {r["assumption"]: r for r in out}
    assert set(by) == {"a.x.same", "a.x.changed", "a.x.new", "b.y.other"}
    assert by["a.x.same"]["review_status"] == "verified"
    assert by["a.x.changed"]["value"] == "20"
    assert by["a.x.changed"]["review_status"] == "unreviewed" and by["a.x.changed"]["reviewer"] == ""
    assert by["a.x.new"]["id"] == row_id("a.x.new") and by["a.x.new"]["review_status"] == "unreviewed"
    assert by["b.y.other"]["value"] == "9" and by["b.y.other"]["reviewer"] == "nigel"


def test_row_ids_follow_the_existing_convention() -> None:
    assert row_id("agriculture.base_year_volume.by_country.ZAF.value") == "LOC-60de01133f61"
