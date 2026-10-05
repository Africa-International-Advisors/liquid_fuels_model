"""Command-line entry point.

Usage:
    python -m lfm run --vintage 2026 [--scenario high_demand|low_demand]

Runs all six demand segments, supply and balance with governance checks and provenance.
The check subcommand audits declared inputs; --strict also rejects open exceptions.
"""
from __future__ import annotations

import argparse
import json
import getpass
import platform
from importlib.metadata import version
import hashlib
import subprocess
import sys

import pandas as pd

from .assumptions import YamlDirectoryProvider
from .config import Paths
from .assumptions.snapshot import SnapshotProvider
from .governance import check, input_fingerprints, open_exceptions
import yaml
from .model.demand import agriculture, aviation, generation, industrial, marine, vehicles
from .reporting.aggregate import aggregate_volumes
from .run import Run
from .model.supply.flows import compute_balance, compute_supply


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
    check_p = sub.add_parser("check", help="Audit assumption register and exceptions.")
    check_p.add_argument("--vintage", default="2026")
    check_p.add_argument("--strict", action="store_true", help="Also fail on open exceptions.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    paths = Paths.default()
    if args.cmd == "check":
        ok, problems = check(paths, args.vintage, strict=args.strict)
        for problem in problems:
            print(problem, file=sys.stderr)
        if ok:
            print(f"Governance coverage passed; {len(open_exceptions(paths, args.vintage))} open exceptions. Output remains draft while exceptions are open.")
        return 0 if ok else 1
    if args.cmd != "run":
        return 2
    ok, problems = check(paths, args.vintage)
    if not ok:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    meta = yaml.safe_load((paths.vintage_dir(args.vintage) / "_meta.yaml").read_text(encoding="utf-8"))
    if args.scenario not in {s["name"] for s in meta["scenarios"]}:
        print("Scenario is not defined in vintage metadata", file=sys.stderr)
        return 1

    run = Run(vintage=args.vintage, scenario=args.scenario)
    paths = Paths.default()
    source_provider = YamlDirectoryProvider(paths)
    provider = SnapshotProvider(source_provider, run)

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
    provisional_flags = _detect_provisional(source_provider, run)

    out_dir = paths.runs_dir / run.tag()
    if out_dir.exists():
        out_dir = out_dir / run.executed_at.strftime("%Y%m%dT%H%M%S%fZ")
    out_dir.mkdir(parents=True, exist_ok=False)
    monthly_path = out_dir / "demand_monthly.csv"
    annual_path = out_dir / "demand_annual.csv"
    balance_path = out_dir / "balance_annual.csv"
    provenance_path = out_dir / "provenance.json"

    monthly.to_csv(monthly_path, index=False)
    annual.to_csv(annual_path, index=False)
    balance_annual.to_csv(balance_path, index=False)
    git_status = _git(paths, "status", "--porcelain")
    provenance_path.write_text(
        json.dumps(
            {
                "run_tag": run.tag(),
                "engine_commit": _git(paths, "rev-parse", "HEAD"),
                "working_tree_dirty": bool(git_status) if git_status is not None else None,
                "python_version": platform.python_version(),
                "runtime_packages": {name: version(name) for name in ("numpy", "pandas", "PyYAML", "openpyxl")},
                "executed_by": getpass.getuser(),
                "source_repo_ref": meta.get("source_repo_ref"),
                "open_exceptions": [e["id"] for e in open_exceptions(paths, run.vintage)],
                "status": "provisional" if open_exceptions(paths, run.vintage) else "draft-awaiting-review",
                "input_sha256": input_fingerprints(paths, run.vintage),
                "code_sha256": {str(p.relative_to(paths.repo_root)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted((paths.repo_root / "src/lfm").rglob("*.py"))},
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

    if provisional_flags or open_exceptions(paths, run.vintage):
        print(
            "\n[lfm] *** PROVISIONAL OUTPUT -- DO NOT USE FOR DECISIONS ***\n"
            "[lfm] Provisional assumptions and open governance exceptions remain:\n"
            f"[lfm]   {', '.join(provisional_flags)}\n"
            f"[lfm]   Open exceptions: {len(open_exceptions(paths, run.vintage))}\n"
            "[lfm] See docs/methodology/params_sourcing.md for sourcing status.\n",
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


def _git(paths, *args):
    try:
        result = subprocess.run(["git", "-C", str(paths.repo_root), *args], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
