"""Reads assumptions from ``assumptions/<vintage>/<domain>.yaml``.

The vintage directory is treated as immutable once shipped — that's what
makes 2026's run reproducible from 2027 onward. Edits to a shipped vintage
are an audit incident, not a normal workflow.

Resolution rules:

  - Scalar entry (``value:`` field at top level): ``Assumption.value`` is the
    scalar.
  - ``by_country`` entry: ``value`` is the per-country dict (caller indexes by ISO3).
  - ``by_country.<ISO3>.by_scenario`` entries: ``value`` is the entry for the
    Run's scenario (resolved here, not by the caller).
  - ``csv:`` reference: ``value`` is a pandas DataFrame with rows where
    ``scenario in {run.scenario, "shared"}`` (or all rows if no scenario column).
  - Nested entries (e.g., ``efficiency_improvement.diesel`` and
    ``.gasoline``): the loader returns the requested key's resolved value;
    the caller may pass ``"efficiency_improvement.diesel"`` as the key.
"""
from __future__ import annotations

import functools
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from ..config import Paths
from ..run import Run
from ..core.time import ExpansionRule
from .base import Assumption, AssumptionProvider


class YamlDirectoryProvider(AssumptionProvider):
    def __init__(self, paths: Paths | None = None) -> None:
        self._paths = paths or Paths.default()

    # ------------------------------------------------------------------ #
    # Public API

    def get(self, domain: str, key: str, run: Run) -> Assumption:
        doc = self._load_domain(run.vintage, domain)
        node = self._descend(doc, key)
        if node is None:
            raise KeyError(f"{domain}.{key} not found in vintage {run.vintage}")

        value = self._resolve_value(node, run, vintage=run.vintage)
        scenario = run.scenario if not node.get("shared") else None
        return Assumption(
            domain=domain,
            key=key,
            value=value,
            source=str(node.get("source", "unknown")),
            last_updated=_parse_date(node.get("last_updated")),
            vintage=run.vintage,
            scenario=scenario,
            expand=_parse_expand(node.get("expand")),
            units=node.get("units"),
        )

    def list_keys(self, domain: str, vintage: str | None = None) -> list[str]:
        v = vintage or self._latest_vintage()
        doc = self._load_domain(v, domain)
        return [k for k in doc.keys() if not k.startswith("_")]

    # ------------------------------------------------------------------ #
    # Internal: file loading and key descent

    @functools.lru_cache(maxsize=64)
    def _load_domain(self, vintage: str, domain: str) -> dict:
        path = self._paths.vintage_dir(vintage) / f"{domain}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"missing {path}")
        with path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    @staticmethod
    def _descend(doc: dict, dotted_key: str) -> dict | None:
        node: Any = doc
        for part in dotted_key.split("."):
            if not isinstance(node, dict) or part not in node:
                return None
            node = node[part]
        return node if isinstance(node, dict) else None

    # ------------------------------------------------------------------ #
    # Internal: value resolution

    def _resolve_value(self, node: dict, run: Run, *, vintage: str) -> Any:
        # CSV-backed time series
        if "csv" in node:
            return self._load_csv(vintage, node["csv"], run)

        # Per-country slot. Resolve by_scenario nested under a country
        # only if every country entry has by_scenario; otherwise return raw dict.
        if "by_country" in node:
            return self._resolve_by_country(node["by_country"], run)

        # Scalar with `value:` field
        if "value" in node:
            return node["value"]

        # Otherwise return the dict as-is (caller knows the shape).
        return {k: v for k, v in node.items() if k not in _META_KEYS}

    @staticmethod
    def _resolve_by_country(by_country: dict, run: Run) -> dict:
        out: dict[str, Any] = {}
        for iso3, entry in by_country.items():
            if isinstance(entry, dict) and "by_scenario" in entry:
                scenarios = entry["by_scenario"]
                out[iso3] = scenarios.get(run.scenario)
            else:
                out[iso3] = entry
        return out

    def _load_csv(self, vintage: str, rel_path: str, run: Run) -> pd.DataFrame:
        path = self._paths.vintage_dir(vintage) / rel_path
        df = pd.read_csv(path)
        if "scenario" in df.columns:
            mask = df["scenario"].isin([run.scenario, "shared"])
            df = df.loc[mask].reset_index(drop=True)
        return df


# --------------------------------------------------------------------------- #
# Helpers

# Keys that describe an assumption rather than carry its value; stripped from
# any returned dict so callers see only the substantive payload.
_META_KEYS = {
    "source",
    "last_updated",
    "scenarios",
    "shared",
    "expand",
    "units",
    "provisional",
    "needs_verification",
}


def _parse_date(v: Any) -> date:
    if v is None:
        return date.min
    if isinstance(v, date) and not isinstance(v, datetime):
        return v
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, str):
        return date.fromisoformat(v)
    raise TypeError(f"unrecognised last_updated value: {v!r}")


def _parse_expand(v: Any) -> ExpansionRule | None:
    if v is None:
        return None
    if not isinstance(v, dict):
        raise TypeError(f"expand must be a dict; got {v!r}")
    return ExpansionRule(kind=v["kind"], seasonal_index=v.get("seasonal_index"))
