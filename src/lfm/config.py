"""Filesystem layout and path resolution.

Centralises where the model looks for assumptions, raw data, and writes
outputs. Override via env vars (``LFM_ASSUMPTIONS_DIR``, ``LFM_DATA_DIR``,
``LFM_RUNS_DIR``) or by passing explicit paths to the loader functions.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _repo_root() -> Path:
    # src/lfm/config.py -> repo root is two parents up from src/lfm
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Paths:
    repo_root: Path
    assumptions_dir: Path
    data_dir: Path
    runs_dir: Path

    @classmethod
    def default(cls) -> "Paths":
        root = _repo_root()
        return cls(
            repo_root=root,
            assumptions_dir=Path(os.getenv("LFM_ASSUMPTIONS_DIR", root / "assumptions")),
            data_dir=Path(os.getenv("LFM_DATA_DIR", root / "data")),
            runs_dir=Path(os.getenv("LFM_RUNS_DIR", root / "runs")),
        )

    def vintage_dir(self, vintage: str) -> Path:
        return self.assumptions_dir / vintage
