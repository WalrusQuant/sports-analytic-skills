"""NHL team-win walk-forward pipeline."""

from __future__ import annotations

from typing import Any

from sports_ds.data.nhl import load_nhl_team_game_panel
from sports_ds.pipelines.team_win import format_team_win_report, run_loader_win_pipeline


def run_nhl_win_pipeline(
    seasons: list[int] | None = None,
    min_train_seasons: int = 1,
    min_pre_games: int = 5,
) -> dict[str, Any]:
    if seasons is None:
        seasons = [2023, 2024]
    return run_loader_win_pipeline(
        load_nhl_team_game_panel,
        seasons,
        sport="nhl",
        min_train_seasons=min_train_seasons,
        min_pre_games=min_pre_games,
    )


def format_nhl_win_report(result: dict[str, Any]) -> str:
    return format_team_win_report(result, title="NHL team-win model pipeline")
