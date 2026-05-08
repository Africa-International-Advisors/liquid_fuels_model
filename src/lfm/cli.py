"""Command-line entry point.

Usage:
    python -m lfm run --vintage 2026 [--scenario reference]
"""
from __future__ import annotations

import argparse
import sys

from .run import Run


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lfm", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Execute a model run.")
    run_p.add_argument("--vintage", required=True, help="Assumption vintage tag, e.g. 2026")
    run_p.add_argument("--scenario", default="reference", help="Scenario name (v1: reference)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.cmd == "run":
        run = Run(vintage=args.vintage, scenario=args.scenario)
        print(f"[lfm] prepared run {run.tag()} -- engine not implemented yet", file=sys.stderr)
        return 0
    return 2
