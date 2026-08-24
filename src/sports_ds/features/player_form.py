"""Time-safe pre-game player form features."""

from __future__ import annotations

import pandas as pd


PLAYER_TARGET_DEFAULT = "fantasy_points_ppr"


def add_pregame_player_form_features(
    panel: pd.DataFrame,
    *,
    windows: list[int] | None = None,
    ewma_spans: list[int] | None = None,
    stat_cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    Add shifted expanding/rolling/EWMA player form features.

    Entity key: player_id. Sort: player, season, week, gameday, game_id.
    """
    if windows is None:
        windows = [3, 5]
    if ewma_spans is None:
        ewma_spans = [5]
    if stat_cols is None:
        stat_cols = [
            "fantasy_points_ppr",
            "fantasy_points",
            "targets",
            "receptions",
            "receiving_yards",
            "carries",
            "rushing_yards",
            "attempts",
            "passing_yards",
            "target_share",
        ]

    df = panel.sort_values(["player_id", "season", "week", "gameday", "game_id"]).copy()
    g = df.groupby("player_id", group_keys=False)

    df["pre_games_played"] = g["player_id"].apply(lambda s: s.shift(1).expanding().count())

    for col in stat_cols:
        if col not in df.columns:
            continue
        df[f"pre_{col}"] = g[col].apply(lambda s: s.shift(1).expanding().mean())
        for w in windows:
            df[f"roll{w}_{col}"] = g[col].apply(
                lambda s, ww=w: s.shift(1).rolling(ww, min_periods=1).mean()
            )
        for sp in ewma_spans:
            df[f"ewma{sp}_{col}"] = g[col].apply(
                lambda s, span=sp: s.shift(1).ewm(span=span, min_periods=1).mean()
            )

    if "is_home" in df.columns:
        # keep as known-at-T feature
        pass
    if "week" in df.columns:
        df["season_week"] = pd.to_numeric(df["week"], errors="coerce")

    # position one-hot lite flags (known pre-game)
    if "position" in df.columns:
        for pos in ("QB", "RB", "WR", "TE"):
            df[f"pos_{pos}"] = (df["position"] == pos).astype(int)

    return df


DEFAULT_PLAYER_FEATURE_COLS = [
    "is_home",
    "season_week",
    "pre_games_played",
    "pre_fantasy_points_ppr",
    "roll3_fantasy_points_ppr",
    "roll5_fantasy_points_ppr",
    "ewma5_fantasy_points_ppr",
    "pre_targets",
    "roll3_targets",
    "roll5_targets",
    "pre_carries",
    "roll3_carries",
    "pre_attempts",
    "roll3_attempts",
    "pre_receiving_yards",
    "roll3_receiving_yards",
    "pre_rushing_yards",
    "roll3_rushing_yards",
    "pre_passing_yards",
    "roll3_passing_yards",
    "pre_target_share",
    "pos_QB",
    "pos_RB",
    "pos_WR",
    "pos_TE",
]
