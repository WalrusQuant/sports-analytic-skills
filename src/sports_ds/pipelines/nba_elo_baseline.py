"""NBA Elo as-of baseline walk-forward pipeline."""

from __future__ import annotations

from typing import Any

from sports_ds.data.nba import load_nba_team_game_panel
from sports_ds.pipelines.team_elo import format_team_elo_report, run_loader_elo_baseline


def run_nba_elo_baseline(
    seasons: list[int] | None = None,
    min_train_seasons: int = 1,
    k: float = 20.0,
    home_adv: float = 65.0,
) -> dict[str, Any]:
    if seasons is None:
        seasons = [2023, 2024]
    return run_loader_elo_baseline(
        load_nba_team_game_panel,
        seasons,
        sport="nba",
        min_train_seasons=min_train_seasons,
        k=k,
        home_adv=home_adv,
    )


def format_nba_elo_report(result: dict[str, Any]) -> str:
    return format_team_elo_report(result, title="NBA Elo as-of baseline pipeline")
