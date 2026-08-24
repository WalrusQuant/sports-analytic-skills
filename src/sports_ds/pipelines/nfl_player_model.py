"""NFL player-level walk-forward regression (fantasy points / volume targets)."""

from __future__ import annotations

from typing import Any

from sports_ds.data.nfl_players import load_player_game_panel
from sports_ds.features.player_form import (
    DEFAULT_PLAYER_FEATURE_COLS,
    NFL_POSITIONS,
    NFL_STAT_COLS,
    PLAYER_TARGET_DEFAULT,
)
from sports_ds.pipelines.player_model import format_player_report, run_player_pipeline


def run_nfl_player_pipeline(
    seasons: list[int],
    *,
    target_col: str = PLAYER_TARGET_DEFAULT,
    positions: set[str] | None = None,
    min_train_seasons: int = 1,
    min_pre_games: int = 3,
    min_train_rows: int = 200,
    min_test_rows: int = 100,
    feature_cols: list[str] | None = None,
) -> dict[str, Any]:
    pos = positions or set(NFL_POSITIONS)
    panel = load_player_game_panel(seasons, positions=pos)
    return run_player_pipeline(
        panel,
        sport="nfl",
        seasons=seasons,
        target_col=target_col,
        feature_cols=feature_cols or list(DEFAULT_PLAYER_FEATURE_COLS),
        stat_cols=list(NFL_STAT_COLS),
        position_values=tuple(NFL_POSITIONS),
        min_train_seasons=min_train_seasons,
        min_pre_games=min_pre_games,
        min_train_rows=min_train_rows,
        min_test_rows=min_test_rows,
        extra_meta={"positions": sorted(pos)},
    )


def format_nfl_player_report(result: dict[str, Any]) -> str:
    return format_player_report(result, title="NFL player pipeline")
