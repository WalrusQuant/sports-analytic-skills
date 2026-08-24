"""MLB player-level walk-forward pipeline (batters via boxscores)."""

from __future__ import annotations

from typing import Any

from sports_ds.data.mlb_players import load_mlb_player_game_panel
from sports_ds.features.player_form import (
    DEFAULT_MLB_PLAYER_FEATURE_COLS,
    MLB_POSITIONS,
    MLB_STAT_COLS,
)
from sports_ds.pipelines.player_model import format_player_report, run_player_pipeline


def run_mlb_player_pipeline(
    seasons: list[int],
    *,
    target_col: str = "fantasy_points",
    positions: set[str] | None = None,
    min_train_seasons: int = 1,
    min_pre_games: int = 5,
    min_pa: float = 1.0,
    min_train_rows: int = 500,
    min_test_rows: int = 200,
    max_games: int | None = None,
    feature_cols: list[str] | None = None,
) -> dict[str, Any]:
    # default: hitters only (exclude pure P unless asked)
    if positions is None:
        positions = {p for p in MLB_POSITIONS if p != "P"}
    panel = load_mlb_player_game_panel(
        seasons,
        positions=positions,
        min_pa=min_pa,
        max_games=max_games,
    )
    result = run_player_pipeline(
        panel,
        sport="mlb",
        seasons=seasons,
        target_col=target_col,
        feature_cols=feature_cols or list(DEFAULT_MLB_PLAYER_FEATURE_COLS),
        stat_cols=list(MLB_STAT_COLS),
        position_values=tuple(sorted(positions)),
        min_train_seasons=min_train_seasons,
        min_pre_games=min_pre_games,
        min_train_rows=min_train_rows,
        min_test_rows=min_test_rows,
        extra_meta={
            "positions": sorted(positions),
            "min_pa": min_pa,
            "max_games": max_games,
        },
    )
    return result


def format_mlb_player_report(result: dict[str, Any]) -> str:
    return format_player_report(result, title="MLB player pipeline (batters)")
