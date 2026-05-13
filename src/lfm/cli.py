"""Command-line entry point.

Usage:
    python -m lfm run --vintage 2026 [--scenario high_demand|low_demand]

Currently runs the vehicles segment end-to-end and writes per-run CSVs to
``runs/<vintage>-<scenario>-v<version>/``. Other segments still raise
NotImplementedError when their compute is invoked directly.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from .assumptions import YamlDirectoryProvider
from .config import Paths
from .demand import agriculture, aviation, generation, industrial, marine, vehicles
from .output.aggregate import aggregate_volumes
from .run import Run
from .supply.flows import compute_balance, compute_supply


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lfm", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Execute a model run.")
    run_p.add_argument("--vintage", required=True, help="Assumption vintage tag, e.g. 2026")
    run_p.add_argument(
        "--scenario",
        default="high_demand",
        choices=["high_demand", "low_demand"],
        help="Scenario name (v1: high_demand or low_demand)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.cmd != "run":
        return 2

    run = Run(vintage=args.vintage, scenario=args.scenario)
    paths = Paths.default()
    provider = YamlDirectoryProvider(paths)

    print(f"[lfm] {run.tag()}: starting", file=sys.stderr)

    segment_modules = [vehicles, aviation, generation, industrial, marine, agriculture]
    segments_run: list[str] = []
    frames: list = []
    for mod in segment_modules:
        print(f"[lfm]   computing {mod.name} segment...", file=sys.stderr)
        result = mod.compute_demand(provider, run)
        if not result.frame.empty:
            frames.append(result.frame)
        segments_run.append(mod.name)
        print(f"[lfm]     -> {len(result.frame):,} monthly rows", file=sys.stderr)

    monthly = (
        pd.concat(frames, ignore_index=True)
        if frames
        else pd.DataFrame(columns=["country", "product", "period", "volume"])
    )
    annual = aggregate_volumes(monthly)
    print(f"[lfm]   total: {len(monthly):,} monthly rows -> {len(annual):,} annual rows",
          file=sys.stderr)

    # Supply + demand-supply balance.
    print("[lfm]   computing supply (refineries)...", file=sys.stderr)
    supply_annual = compute_supply(provider, run)
    print(f"[lfm]     -> {len(supply_annual):,} annual rows", file=sys.stderr)
    balance_annual = compute_balance(monthly, supply_annual)
    print(f"[lfm]   balance: {len(balance_annual):,} rows (demand-supply-deficit)",
          file=sys.stderr)

    # Banner: any provisional inputs should leave a loud mark on output.
    provisional_flags = _detect_provisional(provider, run)

    out_dir = paths.runs_dir / run.tag()
    out_dir.mkdir(parents=True, exist_ok=True)
    monthly_path = out_dir / "demand_monthly.csv"
    annual_path = out_dir / "demand_annual.csv"
    balance_path = out_dir / "balance_annual.csv"
    provenance_path = out_dir / "provenance.json"

    monthly.to_csv(monthly_path, index=False)
    annual.to_csv(annual_path, index=False)
    balance_annual.to_csv(balance_path, index=False)
    provenance_path.write_text(
        json.dumps(
            {
                "run_tag": run.tag(),
                "vintage": run.vintage,
                "scenario": run.scenario,
                "model_version": run.model_version,
                "executed_at": run.executed_at.isoformat(),
                "segments_run": segments_run,
                "supply_run": True,
                "provisional_inputs": provisional_flags,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    if provisional_flags:
        print(
            "\n[lfm] *** PROVISIONAL OUTPUT -- DO NOT USE FOR DECISIONS ***\n"
            "[lfm] The following vehicle parameters are literature-range placeholders:\n"
            f"[lfm]   {', '.join(provisional_flags)}\n"
            "[lfm] See docs/params_sourcing.md for sourcing status.\n",
            file=sys.stderr,
        )

    for p in (monthly_path, annual_path, balance_path, provenance_path):
        print(f"[lfm] wrote {p.relative_to(paths.repo_root).as_posix()}",
              file=sys.stderr)
    print(f"[lfm] {run.tag()}: done", file=sys.stderr)
    return 0


def _detect_provisional(provider: YamlDirectoryProvider, run: Run) -> list[str]:
    """Return the list of YAML keys still flagged provisional across all segments."""
    domains = ["vehicles", "industrial", "marine", "agriculture"]
    out: list[str] = []
    for domain in domains:
        try:
            doc = provider._load_domain(run.vintage, domain)  # noqa: SLF001
        except FileNotFoundError:
            continue
        for key, node in doc.items():
            if isinstance(node, dict) and node.get("provisional"):
                out.append(f"{domain}.{key}")
    return out
