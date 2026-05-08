"""Reads assumptions from ``assumptions/<vintage>/<domain>.yaml``.

The vintage directory is treated as immutable once shipped — that's what
makes 2026's run reproducible from 2027 onward. Edits to a shipped vintage
are an audit incident, not a normal workflow.
"""
from __future__ import annotations

from pathlib import Path

from ..config import Paths
from ..run import Run
from .base import Assumption, AssumptionProvider


class YamlDirectoryProvider(AssumptionProvider):
    def __init__(self, paths: Paths | None = None) -> None:
        self._paths = paths or Paths.default()

    def get(self, domain: str, key: str, run: Run) -> Assumption:
        """Resolve ``(domain, key)`` from the run's vintage directory.

        Implementation deferred — interface is fixed so demand modules
        can be written against it before the loader is filled in.
        """
        raise NotImplementedError("YAML loader to be implemented in v1 build-out")

    def list_keys(self, domain: str) -> list[str]:
        raise NotImplementedError("YAML loader to be implemented in v1 build-out")

    def _vintage_path(self, run: Run) -> Path:
        return self._paths.vintage_dir(run.vintage)
