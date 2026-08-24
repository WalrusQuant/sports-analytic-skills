"""MLB team-margin walk-forward pipeline."""

from __future__ import annotations

from typing import Any

from sports_ds.data.mlb import load_mlb_team_game_panel
from sports_ds.pipelines.team_margin import format_team_margin_report, run_loader_margin_pipeline


def run_mlb_margin_pipeline(
    seasons: list[int] | None = None,
    min_train_seasons: int = 1,
    min_pre_games: int = 10,
) -> dict[str, Any]:
    if seasons is None:
        seasons = [2023, 2024]
    return run_loader_margin_pipeline(
        load_mlb_team_game_panel,
        seasons,
        sport="mlb",
        min_train_seasons=min_train_seasons,
        min_pre_games=min_pre_games,
    )


def format_mlb_margin_report(result: dict[str, Any]) -> str:
    return format_team_margin_report(result, title="MLB team-margin model pipeline")
