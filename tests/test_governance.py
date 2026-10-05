"""Governance must catch undocumented changes without certifying draft inputs."""
import csv
import shutil

import pytest
import yaml

from lfm.config import Paths
from lfm.governance import check
from lfm.assumptions import YamlDirectoryProvider
from lfm.assumptions.snapshot import SnapshotProvider
from lfm.run import Run


@pytest.fixture
def isolated(tmp_path):
    root = Paths.default().repo_root
    shutil.copytree(root / "assumptions", tmp_path / "assumptions")
    shutil.copytree(root / "governance", tmp_path / "governance")
    return Paths(tmp_path, tmp_path / "assumptions", tmp_path / "external/data", tmp_path / "runs")


def test_draft_coverage_passes_but_release_does_not():
    assert check()[0]
    ok, issues = check(strict=True)
    assert not ok
    assert any("open exceptions" in issue for issue in issues)


def test_changed_scalar_is_rejected(isolated):
    path = isolated.vintage_dir("2026") / "macro.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    doc["crude_oil_litres_per_barrel"]["value"] += 1
    path.write_text(yaml.safe_dump(doc), encoding="utf-8")
    assert any("value differs" in issue for issue in check(isolated)[1])


def test_changed_csv_is_rejected(isolated):
    path = isolated.vintage_dir("2026") / "timeseries/gdp_per_capita.csv"
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    rows[0]["value"] = "1"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    assert not check(isolated)[0]


def test_missing_register_row_is_rejected(isolated):
    path = isolated.repo_root / "governance/assumption_register.csv"
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    assert any("missing register row" in issue for issue in check(isolated)[1])


def test_expired_exception_is_rejected(isolated):
    path = isolated.repo_root / "governance/exception_log.csv"
    text = path.read_text(encoding="utf-8").replace("2026-11-12", "2000-01-01")
    path.write_text(text, encoding="utf-8")
    assert any("expired" in issue for issue in check(isolated)[1])


def test_snapshot_never_reads_source_after_loading(monkeypatch):
    run = Run(vintage="2026", scenario="high_demand")
    source = YamlDirectoryProvider()
    snapshot = SnapshotProvider(source, run)
    def fail(*args, **kwargs):
        raise AssertionError("Model accessed file provider")
    monkeypatch.setattr(source, "get", fail)
    from lfm.model.demand import vehicles
    assert not vehicles.compute_demand(snapshot, run).frame.empty
    with pytest.raises(ValueError):
        snapshot.get("macro", "gdp", Run(vintage="2026", scenario="low_demand"))


def test_undeclared_bare_number_is_rejected(isolated):
    path = isolated.vintage_dir("2026") / "macro.yaml"
    path.write_text(path.read_text(encoding="utf-8") + "\nrogue_input: 42\n", encoding="utf-8")
    assert not check(isolated)[0]


def test_cli_stamps_provenance_and_preserves_previous_run(isolated, monkeypatch):
    import json
    from lfm.cli import main
    monkeypatch.setattr(Paths, "default", classmethod(lambda cls: isolated))
    args = ["run", "--vintage", "2026", "--scenario", "high_demand"]
    assert main(args) == 0
    directory = isolated.runs_dir / "2026-high_demand-v0.1.0"
    original = (directory / "provenance.json").read_bytes()
    stamp = json.loads(original)
    assert stamp["status"] == "provisional"
    assert stamp["open_exceptions"]
    assert stamp["executed_by"]
    assert stamp["input_sha256"]
    assert stamp["python_version"]
    assert main(args) == 0
    assert (directory / "provenance.json").read_bytes() == original
    assert len(list(directory.glob("*/provenance.json"))) == 1
