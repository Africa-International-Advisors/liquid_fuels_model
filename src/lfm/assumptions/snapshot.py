"""Resolve file-backed inputs before entering the model engine."""
from ..governance import assumption_blocks


class SnapshotProvider:
    def __init__(self, source, run):
        self._run = (run.vintage, run.scenario)
        self._values = {}
        for path in sorted(source._paths.vintage_dir(run.vintage).glob("*.yaml")):
            if path.stem.startswith("_"):
                continue
            for key, _ in assumption_blocks(source._load_domain(run.vintage, path.stem)):
                self._values[path.stem, key] = source.get(path.stem, key, run)

    def get(self, domain, key, run):
        if (run.vintage, run.scenario) != self._run:
            raise ValueError("Snapshot belongs to a different vintage or scenario")
        return self._values[domain, key]

    def list_keys(self, domain):
        return [key for d, key in self._values if d == domain]
