"""NFL Elo as-of baseline walk-forward evaluation."""

from __future__ import annotations

from typing import Any

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.pipelines.team_elo import format_team_elo_report, run_loader_elo_baseline

FEATURE_COLS = ["is_home", "elo_diff"]


def run_nfl_elo_baseline(
    seasons: list[int] | None = None,
    min_train_seasons: int = 2,
    k: float = 20.0,
    home_adv: float = 65.0,
) -> dict[str, Any]:
    if seasons is None:
        seasons = list(range(2018, 2025))
    return run_loader_elo_baseline(
        load_team_game_panel,
        seasons,
        sport="nfl",
        min_train_seasons=min_train_seasons,
        k=k,
        home_adv=home_adv,
        min_train_rows=200,
        min_test_rows=50,
    )


def format_elo_report(result: dict[str, Any]) -> str:
    return format_team_elo_report(result, title="NFL Elo as-of baseline pipeline")
