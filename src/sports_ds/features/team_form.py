"""Time-safe pre-game team form features."""

from __future__ import annotations

import pandas as pd


def add_pregame_form_features(panel: pd.DataFrame, windows: list[int] | None = None) -> pd.DataFrame:
    """
    Add expanding/rolling pre-game form features.

    All features use only prior games for that team (shift 1).
    """
    if windows is None:
        windows = [3, 5]

    df = panel.sort_values(["team", "season", "week", "gameday", "game_id"]).copy()
    g = df.groupby("team", group_keys=False)

    # career/season-to-date style expanding means before current game
    df["pre_win_pct"] = g["won"].apply(lambda s: s.shift(1).expanding().mean())
    df["pre_avg_pf"] = g["points_for"].apply(lambda s: s.shift(1).expanding().mean())
    df["pre_avg_pa"] = g["points_against"].apply(lambda s: s.shift(1).expanding().mean())
    df["pre_avg_diff"] = g["point_diff"].apply(lambda s: s.shift(1).expanding().mean())
    df["pre_games_played"] = g["won"].apply(lambda s: s.shift(1).expanding().count())

    for w in windows:
        df[f"roll{w}_win_pct"] = g["won"].apply(lambda s, ww=w: s.shift(1).rolling(ww, min_periods=1).mean())
        df[f"roll{w}_diff"] = g["point_diff"].apply(
            lambda s, ww=w: s.shift(1).rolling(ww, min_periods=1).mean()
        )

    # opponent pre-game form via self-join on opponent prior features
    opp_cols = [
        "game_id",
        "team",
        "pre_win_pct",
        "pre_avg_diff",
        "pre_games_played",
        "roll3_win_pct",
        "roll3_diff",
        "roll5_win_pct",
        "roll5_diff",
    ]
    opp = df[opp_cols].rename(
        columns={
            "team": "opponent",
            "pre_win_pct": "opp_pre_win_pct",
            "pre_avg_diff": "opp_pre_avg_diff",
            "pre_games_played": "opp_pre_games_played",
            "roll3_win_pct": "opp_roll3_win_pct",
            "roll3_diff": "opp_roll3_diff",
            "roll5_win_pct": "opp_roll5_win_pct",
            "roll5_diff": "opp_roll5_diff",
        }
    )
    df = df.merge(opp, on=["game_id", "opponent"], how="left")

    df["feature_win_pct_diff"] = df["pre_win_pct"] - df["opp_pre_win_pct"]
    df["feature_diff_diff"] = df["pre_avg_diff"] - df["opp_pre_avg_diff"]
    df["feature_roll3_win_diff"] = df["roll3_win_pct"] - df["opp_roll3_win_pct"]
    df["feature_roll5_diff_diff"] = df["roll5_diff"] - df["opp_roll5_diff"]

    return df
