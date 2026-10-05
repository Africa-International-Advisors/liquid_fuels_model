"""Audit declared inputs, CSV coverage, original-source evidence and model reads.

Runs both defined scenarios, recording snapshot requests after preloading.
This establishes block access, not the influence of every row or scalar.
It never marks source figures verified or modifies model inputs/registers.
Run: python -m lfm.scripts.audit_source_inputs --vintage 2026
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import inspect
import json
import os
from pathlib import Path

import yaml

from lfm import cli
from lfm.assumptions.snapshot import SnapshotProvider
from lfm.config import Paths
from lfm.governance import assumption_blocks, inventory, read_rows


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_records(value, metadata, context=""):
    """Find original document references without mistaking CSV inputs for originals."""
    if isinstance(value, dict):
        if "url" in value or "sha256" in value:
            local = value.get("file", value.get("local", value.get("path", "")))
            yield {"metadata": metadata, "context": context, "file": str(local),
                   "url": str(value.get("url", "")), "sha256": str(value.get("sha256", ""))}
        for key, item in value.items():
            yield from source_records(item, metadata, f"{context}.{key}".strip("."))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from source_records(item, metadata, f"{context}[{index}]")


def write_csv(path, rows, headers):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vintage", default="2026")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    paths = Paths.default()
    base = paths.vintage_dir(args.vintage)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = (args.output_dir or paths.runs_dir / f"source_audit_{stamp}").resolve()
    out.mkdir(parents=True, exist_ok=False)
    reads = defaultdict(set)
    runs = []

    class TracedSnapshot(SnapshotProvider):
        def get(self, domain, key, run):
            caller = inspect.currentframe().f_back
            location = Path(caller.f_code.co_filename)
            label = f"{location.relative_to(paths.repo_root).as_posix()}:{caller.f_lineno}"
            reads[f"{domain}.{key}"].add((run.scenario, label))
            return super().get(domain, key, run)

    original = cli.SnapshotProvider
    prior_runs = os.environ.get("LFM_RUNS_DIR")
    meta = yaml.safe_load((base / "_meta.yaml").read_text(encoding="utf-8"))
    try:
        cli.SnapshotProvider = TracedSnapshot
        os.environ["LFM_RUNS_DIR"] = str(out / "model_runs")
        for scenario in meta["scenarios"]:
            name = scenario["name"]
            try:
                code = cli.main(["run", "--vintage", args.vintage, "--scenario", name])
                runs.append({"scenario": name, "exit_code": code, "error": ""})
            except Exception as exc:
                runs.append({"scenario": name, "exit_code": 1, "error": repr(exc)})
    finally:
        cli.SnapshotProvider = original
        if prior_runs is None:
            os.environ.pop("LFM_RUNS_DIR", None)
        else:
            os.environ["LFM_RUNS_DIR"] = prior_runs

    register = {r["assumption"]: r for r in read_rows(paths.repo_root / "governance/assumption_register.csv") if r["validity"] == args.vintage}
    wide_blocks = set()
    for path in sorted(base.glob("*.yaml")):
        if path.stem.startswith("_"): continue
        for key, node in assumption_blocks(yaml.safe_load(path.read_text(encoding="utf-8")) or {}):
            if "csv" in node:
                with (base / node["csv"]).open(encoding="utf-8-sig", newline="") as stream:
                    if "value" not in (csv.DictReader(stream).fieldnames or []):
                        wide_blocks.add(f"{path.stem}.{key}")
    leaves = []
    for row in inventory(paths, args.vintage):
        record = register.get(row["assumption"], {})
        flags = []
        if not record: flags.append("Missing register row")
        if record.get("review_status") != "verified" or not record.get("reviewer"):
            flags.append("Independent verification not recorded")
        if row["provisional"]: flags.append("Provisional or needs verification")
        if not row["source_date"]: flags.append("Source date missing")
        if row["block"] in wide_blocks:
            flags.append("Wide table: register value does not enumerate individual fields")
        elif row["value"] == "null": flags.append("Null input; inspect country/scenario scope")
        if not reads[row["block"]]: flags.append("Block not requested in traced scenarios")
        leaves.append({**{k: row[k] for k in ["assumption", "block", "value", "unit", "source", "source_date", "owner", "exception_id"]},
                       "review_status": record.get("review_status", ""), "reviewer": record.get("reviewer", ""),
                       "model_access": "Block requested; leaf influence not proven" if reads[row["block"]] else "Not requested in traced scenarios",
                       "flags": "; ".join(flags)})

    blocks = []; declared = defaultdict(list)
    by_block = defaultdict(list)
    for row in leaves: by_block[row["block"]].append(row)
    for path in sorted(base.glob("*.yaml")):
        if path.stem.startswith("_"): continue
        for key, node in assumption_blocks(yaml.safe_load(path.read_text(encoding="utf-8")) or {}):
            name = f"{path.stem}.{key}"
            if "csv" in node: declared[node["csv"]].append(name)
            rows = by_block[name]
            calls = sorted(reads[name])
            blocks.append({"block": name, "input_count": len(rows), "model_access": "Requested by engine" if calls else "Not requested in traced scenarios",
                           "callers": "; ".join(sorted({c[1] for c in calls})), "scenarios": "; ".join(sorted({c[0] for c in calls})),
                           "verified_rows": sum(r["review_status"] == "verified" and bool(r["reviewer"]) for r in rows),
                           "source": str(node.get("source", "")), "source_date": str(node.get("last_updated") or ""),
                           "csv": node.get("csv", ""), "owner": node.get("owner", ""), "exception_id": node.get("exception_id", ""),
                           "flags": "; ".join(sorted({flag for row in rows for flag in row["flags"].split("; ") if flag}))})

    physical = defaultdict(list)
    for path in (paths.repo_root / "external").rglob("*"):
        if path.is_file(): physical[path.name].append(path)
    evidence = []; metadata_errors = []
    for path in sorted(base.rglob("*.sources.yaml")):
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            metadata_errors.append({"file": path.relative_to(paths.repo_root).as_posix(), "error": str(exc), "action": "Repair source metadata syntax; independently verify the referenced original and figures"})
            continue
        for rec in source_records(document, path.relative_to(paths.repo_root).as_posix()):
            candidates = physical.get(Path(rec["file"]).name, []) if rec["file"] else []
            matches = [p for p in candidates if rec["sha256"] and sha256(p) == rec["sha256"]]
            state = "Hash matched; figures not verified" if matches else ("File present; hash absent" if candidates and not rec["sha256"] else ("Hash mismatch" if candidates else "Original not found locally"))
            evidence.append({**rec, "evidence": state, "local_match": "; ".join(p.relative_to(paths.repo_root).as_posix() for p in (matches or candidates))})

    files = []; duplicate_rows = []; provincial_gaps = []; wide_cells = []
    for path in sorted(base.rglob("*.csv")):
        rows = read_rows(path)
        rel = path.relative_to(base).as_posix()
        if rows and "value" not in rows[0]:
            for number, row in enumerate(rows, 2):
                for field, value in row.items():
                    wide_cells.append({"file": rel, "csv_row": number, "field": field, "value": value,
                                       "flags": "Individual field not represented by a register value; independent source reconciliation not recorded"})
        dims = [k for k in (rows[0] if rows else {}) if k not in {"value", "source_file", "source_report", "quarters_reported", "months_reported", "financial_year", "basis"}]
        seen = Counter(tuple(r.get(k, "") for k in dims) for r in rows)
        repeated = sum(n - 1 for n in seen.values())
        for key, count in seen.items():
            if count > 1: duplicate_rows.append({"file": rel, "dimensions": json.dumps(dict(zip(dims, key))), "count": count, "action": "Check missing identifiers or extraction errors; do not sum or deduplicate automatically"})
        names = declared[rel]
        active = any(reads[n] for n in names)
        flags = ["Independent source reconciliation not recorded"]
        if rows and "value" not in rows[0]: flags.append("Wide table: individual fields not represented by register values")
        if not names: flags.append("CSV not declared in an assumption block")
        if repeated: flags.append(f"{repeated} repeated dimension rows; inspect extraction")
        periods = sorted({r.get("period", "") for r in rows} - {""})
        files.append({"file": rel, "rows": len(rows), "blocks": "; ".join(names),
                      "model_access": "Declared block requested; row influence not proven" if active else "Not requested by engine in traced scenarios",
                      "first_period": periods[0] if periods else "", "last_period": periods[-1] if periods else "",
                      "sha256": sha256(path), "repeated_rows": repeated, "flags": "; ".join(flags)})
    q = defaultdict(set)
    for r in read_rows(base / "timeseries/fuel_sales_department_by_province_quarterly.csv"):
        year, quarter = r["period"].split("-Q")
        q[(year, r["province"], r["product"])].add(quarter)
    for r in read_rows(base / "timeseries/fuel_sales_department_by_province.csv"):
        quarters = q[(r["period"], r["province"], r["product"])]
        if quarters != {"1", "2", "3", "4"}:
            provincial_gaps.append({"year": r["period"], "province": r["province"], "product": r["product"], "annual_value": r["value"], "quarters": ",".join(sorted(quarters)), "action": "Reconcile original quarterly tables; distinguish omitted, missing and zero figures"})

    tables = {"assumption_flags": leaves, "assumption_blocks": blocks, "data_files": files, "source_evidence": evidence,
              "duplicate_dimensions": duplicate_rows, "provincial_gaps": provincial_gaps, "model_runs": runs, "metadata_errors": metadata_errors, "wide_table_cells": wide_cells}
    for name, rows in tables.items():
        if rows: write_csv(out / f"{name}.csv", rows, list(rows[0]))
    summary = {"vintage": args.vintage, "executed_at": stamp, "declared_inputs": len(leaves), "blocks": len(blocks),
               "requested_blocks": sum(bool(reads[r["block"]]) for r in blocks), "csv_files": len(files),
               "csv_rows": sum(r["rows"] for r in files), "verified_inputs_recorded": sum(r["review_status"] == "verified" and bool(r["reviewer"]) for r in leaves),
               "source_evidence_states": dict(Counter(r["evidence"] for r in evidence)), "metadata_parse_errors": len(metadata_errors), "provincial_gaps": len(provincial_gaps), "wide_table_fields": len(wide_cells), "runs": runs}
    (out / "audit.json").write_text(json.dumps({"summary": summary, **tables}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Audit files: {out}")
    return 0 if all(r["exit_code"] == 0 for r in runs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
