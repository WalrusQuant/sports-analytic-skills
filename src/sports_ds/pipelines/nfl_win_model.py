"""NFL team-win walk-forward pipeline."""

from __future__ import annotations

from typing import Any

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import DEFAULT_WIN_FEATURE_COLS
from sports_ds.pipelines.team_win import format_team_win_report, run_loader_win_pipeline

FEATURE_COLS = list(DEFAULT_WIN_FEATURE_COLS)


def run_nfl_win_pipeline(
    seasons: list[int] | None = None,
    min_train_seasons: int = 2,
    min_pre_games: int = 3,
) -> dict[str, Any]:
    if seasons is None:
        seasons = list(range(2018, 2025))
    return run_loader_win_pipeline(
        load_team_game_panel,
        seasons,
        sport="nfl",
        min_train_seasons=min_train_seasons,
        min_pre_games=min_pre_games,
        min_train_rows=200,
        min_test_rows=50,
    )


def format_pipeline_report(result: dict[str, Any]) -> str:
    return format_team_win_report(result, title="NFL team-win model pipeline")
