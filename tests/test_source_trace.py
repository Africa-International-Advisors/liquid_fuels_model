"""Every input CSV has a trace entry, and every entry points at a real file and parser."""

import importlib

from lfm.scripts import build_source_trace as trace


def test_every_input_csv_is_traced_and_no_entry_is_stale() -> None:
    rows = trace.build("2026")
    assert [r["dataset"] for r in rows if r["publisher"] == "not traced"] == []
    base = trace.REPO / "assumptions" / "2026"
    assert [rel for rel in trace.TRACE if not (base / rel).exists()] == []


def test_named_source_parsers_exist() -> None:
    missing = []
    for entry in trace.TRACE.values():
        for name in entry[6].replace(";", "/").split("/"):
            module, _, function = name.strip().partition(".")
            if function and " " not in name.strip() and module in {
                "energy_dept", "fiasa", "natis", "naamsa", "eskom", "acsa", "economy", "statssa",
            }:
                if not hasattr(importlib.import_module(f"lfm.sources.{module}"), function):
                    missing.append(name.strip())
    assert missing == []
