"""Provider-agnostic contract for accessing assumptions.

Two principles drive this shape:

* The model identifies an assumption by ``(domain, key)`` plus the active
  ``Run``'s vintage and scenario. Providers resolve that triple to a value.
* Every returned ``Assumption`` carries provenance (source, last_updated)
  so output reports can cite where each number came from.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol

from ..core.time import ExpansionRule
from ..run import Run


@dataclass(frozen=True)
class Assumption:
    """A resolved assumption, with the metadata needed for audit and expansion.

    ``value`` is whatever the provider returns — scalar, dict, pandas Series,
    or DataFrame depending on the domain. Consumers know what shape to expect
    for a given ``(domain, key)``; this class is intentionally untyped on
    value to stay flexible while the v1 segments are wired in.
    """

    domain: str
    key: str
    value: Any
    source: str
    last_updated: date
    vintage: str
    scenario: str | None = None  # None means "shared across scenarios"
    expand: ExpansionRule | None = None
    units: str | None = None


class AssumptionProvider(Protocol):
    """Resolves keyed assumptions for a given Run.

    Implementations:
      - ``YamlDirectoryProvider`` (v1): reads ``assumptions/<vintage>/``
      - future: a provider that fetches from the central assumptions repo
    """

    def get(self, domain: str, key: str, run: Run) -> Assumption: ...

    def list_keys(self, domain: str) -> list[str]: ...
