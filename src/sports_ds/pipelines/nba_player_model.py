"""NBA player-level walk-forward pipeline."""

from __future__ import annotations

from typing import Any

from sports_ds.data.nba_players import load_nba_player_game_panel
from sports_ds.features.player_form import (
    DEFAULT_NBA_PLAYER_FEATURE_COLS,
    NBA_POSITIONS,
    NBA_STAT_COLS,
)
from sports_ds.pipelines.player_model import format_player_report, run_player_pipeline


def run_nba_player_pipeline(
    seasons: list[int],
    *,
    target_col: str = "fantasy_points",
    positions: set[str] | None = None,
    min_train_seasons: int = 1,
    min_pre_games: int = 5,
    min_minutes: float = 5.0,
    min_train_rows: int = 500,
    min_test_rows: int = 200,
    feature_cols: list[str] | None = None,
) -> dict[str, Any]:
    pos = positions
    panel = load_nba_player_game_panel(
        seasons,
        positions=pos,
        min_minutes=min_minutes,
    )
    result = run_player_pipeline(
        panel,
        sport="nba",
        seasons=seasons,
        target_col=target_col,
        feature_cols=feature_cols or list(DEFAULT_NBA_PLAYER_FEATURE_COLS),
        stat_cols=list(NBA_STAT_COLS),
        position_values=tuple(NBA_POSITIONS),
        min_train_seasons=min_train_seasons,
        min_pre_games=min_pre_games,
        min_train_rows=min_train_rows,
        min_test_rows=min_test_rows,
        extra_meta={
            "positions": sorted(pos) if pos else sorted(NBA_POSITIONS),
            "min_minutes": min_minutes,
        },
    )
    return result


def format_nba_player_report(result: dict[str, Any]) -> str:
    return format_player_report(result, title="NBA player pipeline")
