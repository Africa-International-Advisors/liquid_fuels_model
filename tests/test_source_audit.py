"""Audit requests must exclude preload activity and leave shared inputs unchanged."""
import hashlib
import json

from lfm import cli
from lfm.scripts.audit_source_inputs import main, source_records


def test_source_reference_walk_keeps_nested_originals_and_excludes_derived_inputs():
    doc = {"inputs": {"pattern": "reference/pattern.csv"}, "files": {"paper": {"local": "external/paper.pdf", "url": "https://example.org/paper.pdf"}}}
    rows = list(source_records(doc, "evidence.yaml"))
    assert len(rows) == 1
    assert rows[0]["file"] == "external/paper.pdf"
    assert rows[0]["context"] == "files.paper"


def test_audit_excludes_preloaded_sources_and_preserves_inputs(tmp_path, monkeypatch):
    from lfm.config import Paths
    from lfm.run import Run
    paths = Paths.default()
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths.vintage_dir("2026").rglob("*") if p.is_file()}
    original_snapshot = cli.SnapshotProvider

    def one_request(argv):
        scenario = argv[-1]
        run = Run(vintage="2026", scenario=scenario)
        snapshot = cli.SnapshotProvider(cli.YamlDirectoryProvider(paths), run)
        snapshot.get("macro", "gdp_per_capita", run)
        return 0

    monkeypatch.setattr(cli, "main", one_request)
    out = tmp_path / "audit"
    assert main(["--output-dir", str(out)]) == 0
    doc = json.loads((out / "audit.json").read_text(encoding="utf-8"))
    requested = [r["block"] for r in doc["assumption_blocks"] if r["model_access"] == "Requested by engine"]
    assert requested == ["macro.gdp_per_capita"]
    assert cli.SnapshotProvider is original_snapshot
    assert all(hashlib.sha256(p.read_bytes()).hexdigest() == expected for p, expected in before.items())
