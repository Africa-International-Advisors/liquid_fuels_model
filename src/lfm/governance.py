"""Check declared inputs against their owned register and time-bounded exceptions.

Structured YAML blocks inherit a register_id. Every scalar and CSV observation
within that block has its own register row. No input is marked verified by migration.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import date
from pathlib import Path

import yaml

from .config import Paths

PAYLOAD_KEYS = ("value", "by_country", "by_port", "default", "csv")


def assumption_blocks(doc, prefix=""):
    for key, node in doc.items():
        if not isinstance(node, dict):
            raise ValueError(f"{prefix}.{key}: assumption must be a metadata-bearing block")
        name = f"{prefix}.{key}" if prefix else key
        if any(k in node for k in PAYLOAD_KEYS):
            allowed = set(PAYLOAD_KEYS) | {"source", "last_updated", "scenarios", "shared", "expand", "units", "provisional", "needs_verification", "register_id", "exception_id", "owner", "confidence"}
            unknown = set(node) - allowed
            if unknown:
                raise ValueError(f"{name}: undeclared payload fields {sorted(unknown)}")
            yield name, node
        else:
            yield from assumption_blocks(node, name)


def _leaves(value, prefix):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _leaves(item, f"{prefix}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _leaves(item, f"{prefix}[{index}]")
    else:
        yield prefix, value


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)


def inventory(paths=None, vintage="2026"):
    paths = paths or Paths.default()
    base = paths.vintage_dir(vintage)
    for path in sorted(base.glob("*.yaml")):
        if path.stem.startswith("_"):
            continue
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for key, node in assumption_blocks(doc):
            block = f"{path.stem}.{key}"
            values = []
            for payload in PAYLOAD_KEYS:
                if payload not in node:
                    continue
                if payload == "csv":
                    csv_path = (base / node[payload]).resolve()
                    if not csv_path.is_relative_to(base.resolve()):
                        raise ValueError(f"{block}: CSV path leaves vintage directory")
                    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
                        for index, row in enumerate(csv.DictReader(stream), 1):
                            # Include dimension columns in the identity; additions and edits are detected.
                            identity = canonical({k: v for k, v in row.items() if k != "value"})
                            values.append((f"csv[{index}:{identity}]", row.get("value")))
                else:
                    values.extend(_leaves(node[payload], payload))
            for leaf, value in values:
                yield {
                    "assumption": f"{block}.{leaf}", "block": block,
                    "value": canonical(value), "unit": node.get("units", ""),
                    "source": node.get("source", ""),
                    "source_date": str(node.get("last_updated") or ""),
                    "owner": node.get("owner", ""),
                    "confidence": node.get("confidence", ""),
                    "register_group": node.get("register_id", ""),
                    "exception_id": node.get("exception_id", ""),
                    "provisional": bool(node.get("provisional") or node.get("needs_verification")),
                    "validity": str(vintage),
                }


def read_rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def open_exceptions(paths=None, vintage="2026"):
    paths = paths or Paths.default()
    return [r for r in read_rows(paths.repo_root / "governance/exception_log.csv")
            if r.get("status") == "open" and r.get("validity") in (str(vintage), "all")]


def check(paths=None, vintage="2026", *, strict=False):
    paths = paths or Paths.default()
    problems = []
    try:
        rows = [r for r in read_rows(paths.repo_root / "governance/assumption_register.csv")
                if r.get("validity") == str(vintage)]
        exceptions = open_exceptions(paths, vintage)
        inputs = list(inventory(paths, vintage))
        meta = yaml.safe_load((paths.vintage_dir(vintage) / "_meta.yaml").read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return False, [str(exc)]
    if not inputs:
        problems.append("No assumptions found for vintage")
    if not meta.get("owner"):
        problems.append("Vintage metadata has no owner")
    indexed = {r["assumption"]: r for r in rows}
    if len(indexed) != len(rows):
        problems.append("Duplicate assumption paths in register")
    if len({r["id"] for r in rows}) != len(rows):
        problems.append("Duplicate register IDs")
    exception_ids = {r["id"] for r in exceptions}
    if len(exception_ids) != len(exceptions):
        problems.append("Duplicate open exception IDs")
    for row in exceptions:
        for field in ("id", "owner", "reason", "risk", "expiry_trigger", "migration_path", "expires_on"):
            if not row.get(field):
                problems.append(f"Exception {row.get('id')}: missing {field}")
        try:
            if date.fromisoformat(row.get("expires_on", "")) < date.today():
                problems.append(f"Exception {row['id']} expired")
        except ValueError:
            problems.append(f"Exception {row.get('id')}: invalid expiry date")
    for item in inputs:
        label = item["assumption"]
        row = indexed.get(label)
        if row is None:
            problems.append(f"{label}: missing register row")
            continue
        for field in ("value", "unit", "source", "source_date", "register_group", "owner", "confidence"):
            if str(row.get(field, "")) != str(item[field]):
                problems.append(f"{label}: {field} differs from register")
        for field in ("id", "register_group", "owner", "source", "review_status", "confidence"):
            if not row.get(field):
                problems.append(f"{label}: missing {field}")
        ref = item["exception_id"]
        if ref and ref not in exception_ids:
            problems.append(f"{label}: missing or closed exception {ref}")
        if (item["provisional"] or not item["source_date"] or row.get("confidence") == "unassessed") and not ref:
            problems.append(f"{label}: unresolved input needs an exception")
        if row.get("exception_id", "") != ref:
            problems.append(f"{label}: exception reference differs from register")
    extra = set(indexed) - {i["assumption"] for i in inputs}
    problems.extend(f"{key}: stale register row" for key in sorted(extra))
    if strict and any(r.get("review_status") != "verified" or not r.get("reviewer") for r in rows):
        problems.append("Unreviewed register rows prevent release readiness")
    if strict and exceptions:
        problems.append(f"{len(exceptions)} open exceptions prevent release readiness")
    return not problems, problems


def input_fingerprints(paths, vintage):
    base = paths.vintage_dir(vintage)
    files = [p for p in base.rglob("*") if p.is_file()]
    files += list((paths.repo_root / "governance").glob("*.csv"))
    return {str(p.relative_to(paths.repo_root)) if p.is_relative_to(paths.repo_root) else str(p):
            hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
