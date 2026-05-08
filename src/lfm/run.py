"""The Run object — the unit of reproducibility.

Every model execution is identified by ``(model_version, assumption_vintage,
scenario)``. Outputs carry that triple so a 2027 refresh can re-run 2026 logic
on 2026 assumptions and reproduce 2026 numbers exactly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from . import __version__


@dataclass(frozen=True)
class Run:
    """One executable configuration of the model.

    Attributes:
        vintage: Assumption-set vintage tag (e.g. ``"2026"``). Selects which
            ``assumptions/<vintage>/`` directory the provider reads from.
        scenario: Scenario name. v1 ships a single ``"reference"`` scenario;
            the dimension exists so future scenarios add without restructuring.
        model_version: Code version. Defaults to the installed package version.
        executed_at: UTC timestamp the Run was instantiated (provenance only —
            does not affect model output).
    """

    vintage: str
    scenario: str = "reference"
    model_version: str = __version__
    executed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def tag(self) -> str:
        """Short identifier suitable for filenames and output sheets."""
        return f"{self.vintage}-{self.scenario}-v{self.model_version}"
