"""MLB Elo as-of baseline walk-forward pipeline."""

from __future__ import annotations

from typing import Any

from sports_ds.data.mlb import load_mlb_team_game_panel
from sports_ds.pipelines.team_elo import format_team_elo_report, run_loader_elo_baseline


def run_mlb_elo_baseline(
    seasons: list[int] | None = None,
    min_train_seasons: int = 1,
    k: float = 4.0,
    home_adv: float = 20.0,
) -> dict[str, Any]:
    # lower K/home_adv defaults for long MLB season
    if seasons is None:
        seasons = [2023, 2024]
    return run_loader_elo_baseline(
        load_mlb_team_game_panel,
        seasons,
        sport="mlb",
        min_train_seasons=min_train_seasons,
        k=k,
        home_adv=home_adv,
    )


def format_mlb_elo_report(result: dict[str, Any]) -> str:
    return format_team_elo_report(result, title="MLB Elo as-of baseline pipeline")
