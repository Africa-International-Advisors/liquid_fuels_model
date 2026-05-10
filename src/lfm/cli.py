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

from .assumptions import YamlDirectoryProvider
from .config import Paths
from .demand import vehicles
from .output.aggregate import aggregate_volumes
from .run import Run


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

    # v1: vehicles is the only modelled segment with values wired through.
    print("[lfm]   computing vehicles segment...", file=sys.stderr)
    veh = vehicles.compute_demand(provider, run)
    monthly = veh.frame
    print(f"[lfm]     -> {len(monthly):,} monthly rows", file=sys.stderr)

    annual = aggregate_volumes(monthly)
    print(f"[lfm]     -> {len(annual):,} annual rows", file=sys.stderr)

    # Banner: any provisional inputs should leave a loud mark on output.
    provisional_flags = _detect_provisional(provider, run)

    out_dir = paths.runs_dir / run.tag()
    out_dir.mkdir(parents=True, exist_ok=True)
    monthly_path = out_dir / "demand_monthly.csv"
    annual_path = out_dir / "demand_annual.csv"
    provenance_path = out_dir / "provenance.json"

    monthly.to_csv(monthly_path, index=False)
    annual.to_csv(annual_path, index=False)
    provenance_path.write_text(
        json.dumps(
            {
                "run_tag": run.tag(),
                "vintage": run.vintage,
                "scenario": run.scenario,
                "model_version": run.model_version,
                "executed_at": run.executed_at.isoformat(),
                "segments_run": ["vehicles"],
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
            "[lfm] See docs/vehicle_parameters_sourcing.md for sourcing status.\n",
            file=sys.stderr,
        )

    print(f"[lfm] wrote {monthly_path.relative_to(paths.repo_root).as_posix()}",
          file=sys.stderr)
    print(f"[lfm] wrote {annual_path.relative_to(paths.repo_root).as_posix()}",
          file=sys.stderr)
    print(f"[lfm] wrote {provenance_path.relative_to(paths.repo_root).as_posix()}",
          file=sys.stderr)
    print(f"[lfm] {run.tag()}: done", file=sys.stderr)
    return 0


def _detect_provisional(provider: YamlDirectoryProvider, run: Run) -> list[str]:
    """Return the list of vehicle YAML keys still flagged provisional."""
    out: list[str] = []
    domain_doc = provider._load_domain(run.vintage, "vehicles")  # noqa: SLF001
    for key, node in domain_doc.items():
        if isinstance(node, dict) and node.get("provisional"):
            out.append(f"vehicles.{key}")
    return out
