"""Bring the assumption register into line with named input blocks after a deliberate change.

``python -m lfm check`` fails when a YAML value or CSV row differs from
``governance/assumption_register.csv``. That is the intended guard against
silent edits. Once a change has been approved, this command rewrites the
register rows for the blocks named, and only those:

    python -m lfm.scripts.sync_register --vintage 2026 --block industrial.base_year_volume

For each block it:
    * keeps a row whose input is unchanged, with its reviewer and status;
    * updates a row whose value or metadata changed, and resets it to
      ``unreviewed`` with no reviewer, because the reviewed value is gone;
    * adds a row for each new input (``LOC-`` plus the first twelve hex
      characters of the SHA-256 of the assumption path, as existing rows);
    * removes rows whose input no longer exists.

It never touches other blocks, never marks anything reviewed, and never closes
an exception. Use ``--dry-run`` to see the counts without writing.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys

from lfm.config import Paths
from lfm.governance import inventory, read_rows

FIELDS = ["id", "assumption", "register_group", "value", "unit", "source", "source_date", "owner",
          "reviewer", "review_status", "confidence", "validity", "exception_id"]
_FROM_INPUT = ("register_group", "value", "unit", "source", "source_date", "owner", "confidence",
               "exception_id")


def row_id(assumption: str) -> str:
    return "LOC-" + hashlib.sha256(assumption.encode("utf-8")).hexdigest()[:12]


def sync(rows: list[dict], inputs: list[dict], blocks: set[str], vintage: str) -> tuple[list[dict], dict]:
    """Return ``(new_rows, counts)`` with the named blocks reconciled to ``inputs``."""
    wanted = {i["assumption"]: i for i in inputs if i["block"] in blocks}
    prefixes = tuple(block + "." for block in blocks)
    counts = {"kept": 0, "updated": 0, "added": 0, "removed": 0}
    out: list[dict] = []
    seen: set[str] = set()
    for row in rows:
        in_scope = row.get("validity") == vintage and row["assumption"].startswith(prefixes)
        if not in_scope:
            out.append(row)
            continue
        item = wanted.get(row["assumption"])
        if item is None:
            counts["removed"] += 1
            continue
        seen.add(row["assumption"])
        if all(str(row.get(f, "")) == str(item[f]) for f in _FROM_INPUT):
            counts["kept"] += 1
            out.append(row)
            continue
        counts["updated"] += 1
        out.append({**row, **{f: str(item[f]) for f in _FROM_INPUT},
                    "reviewer": "", "review_status": "unreviewed"})
    for assumption, item in wanted.items():
        if assumption in seen:
            continue
        counts["added"] += 1
        out.append({"id": row_id(assumption), "assumption": assumption,
                    **{f: str(item[f]) for f in _FROM_INPUT},
                    "reviewer": "", "review_status": "unreviewed", "validity": vintage})
    return out, counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--block", action="append", required=True,
                        help="block to reconcile, e.g. supply.refinery_utilisation (repeatable)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    paths = Paths.default()
    register = paths.repo_root / "governance" / "assumption_register.csv"
    inputs = list(inventory(paths, args.vintage))
    known = {i["block"] for i in inputs}
    unknown = sorted(set(args.block) - known)
    if unknown:
        sys.exit(f"no such block in vintage {args.vintage}: {unknown}")

    rows, counts = sync(read_rows(register), inputs, set(args.block), args.vintage)
    print(f"[register] {', '.join(args.block)}: {counts}", file=sys.stderr)
    if args.dry_run:
        return 0
    with register.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
