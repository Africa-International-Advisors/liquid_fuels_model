"""Template-driven xlsx writer.

Stakeholders consume the model as an xlsx. This module populates a
designed template (named ranges + sheet placeholders) rather than
emitting a workbook from scratch, so analysts can re-skin the deliverable
without touching Python.

Template lives at ``assumptions/<vintage>/output_template.xlsx`` (or a
shared template path overriden via env). The Run tag is written into a
provenance sheet so any output can be traced back to its inputs.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..run import Run


def write_workbook(
    annual_demand: pd.DataFrame,
    flows: pd.DataFrame,
    run: Run,
    output_path: Path,
    template_path: Path | None = None,
) -> Path:
    """Populate the xlsx template with this run's outputs. To be implemented."""
    raise NotImplementedError("xlsx writer to be implemented in v1 build-out")
