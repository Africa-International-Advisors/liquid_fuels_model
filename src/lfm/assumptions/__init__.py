"""Assumption provider — the seam between model code and assumption sources.

The model never reads assumption files directly; it asks an
``AssumptionProvider`` for keyed values. v1 ships ``YamlDirectoryProvider``
which reads ``assumptions/<vintage>/``. Swapping in a remote/central-repo
provider later is a one-class change with no model-code impact.
"""
from .base import Assumption, AssumptionProvider
from .yaml_provider import YamlDirectoryProvider

__all__ = ["Assumption", "AssumptionProvider", "YamlDirectoryProvider"]
