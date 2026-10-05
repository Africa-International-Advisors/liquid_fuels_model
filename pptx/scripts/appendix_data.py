"""Consume the existing model reconciliation for the presentation appendix."""
from pathlib import Path

from lfm.assumptions import YamlDirectoryProvider
from lfm.config import Paths
from lfm.run import Run
from lfm.scripts.compare_history import build_comparison, load_history, model_historical


def current_comparison(output: Path):
    paths = Paths.default()
    scenario = 'high_demand'
    result = build_comparison(
        load_history(paths),
        model_historical(Run(vintage='2026', scenario=scenario), YamlDirectoryProvider(paths)),
        scenario,
    )
    output.mkdir(parents=True, exist_ok=True)
    result.to_csv(output / 'historical_comparison.csv', index=False)
    return result[result.year == 2024].set_index('product')
