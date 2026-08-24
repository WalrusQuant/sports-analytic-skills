"""Time-safe pre-game team form features."""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_pregame_form_features(
    panel: pd.DataFrame,
    windows: list[int] | None = None,
    *,
    ewma_spans: list[int] | None = None,
    include_rest: bool = True,
    include_home_split: bool = True,
    include_calendar: bool = True,
) -> pd.DataFrame:
    """
    Add expanding/rolling/EWMA pre-game form features.

    All features use only prior games for that team (shift 1).
    """
    if windows is None:
        windows = [3, 5]
    if ewma_spans is None:
        ewma_spans = [5]

    df = panel.sort_values(["team", "season", "week", "gameday", "game_id"]).copy()
    g = df.groupby("team", group_keys=False)

    df["pre_win_pct"] = g["won"].apply(lambda s: s.shift(1).expanding().mean())
    df["pre_avg_pf"] = g["points_for"].apply(lambda s: s.shift(1).expanding().mean())
    df["pre_avg_pa"] = g["points_against"].apply(lambda s: s.shift(1).expanding().mean())
    df["pre_avg_diff"] = g["point_diff"].apply(lambda s: s.shift(1).expanding().mean())
    df["pre_games_played"] = g["won"].apply(lambda s: s.shift(1).expanding().count())

    for w in windows:
        df[f"roll{w}_win_pct"] = g["won"].apply(
            lambda s, ww=w: s.shift(1).rolling(ww, min_periods=1).mean()
        )
        df[f"roll{w}_diff"] = g["point_diff"].apply(
            lambda s, ww=w: s.shift(1).rolling(ww, min_periods=1).mean()
        )
        df[f"roll{w}_pf"] = g["points_for"].apply(
            lambda s, ww=w: s.shift(1).rolling(ww, min_periods=1).mean()
        )
        df[f"roll{w}_pa"] = g["points_against"].apply(
            lambda s, ww=w: s.shift(1).rolling(ww, min_periods=1).mean()
        )

    for span in ewma_spans:
        df[f"ewma{span}_win"] = g["won"].apply(
            lambda s, sp=span: s.shift(1).ewm(span=sp, min_periods=1).mean()
        )
        df[f"ewma{span}_diff"] = g["point_diff"].apply(
            lambda s, sp=span: s.shift(1).ewm(span=sp, min_periods=1).mean()
        )

    if include_rest and "gameday" in df.columns:
        gd = pd.to_datetime(df["gameday"], errors="coerce")
        prev_gd = g["gameday"].shift(1)
        prev_gd = pd.to_datetime(prev_gd, errors="coerce")
        df["rest_days"] = (gd - prev_gd).dt.days
        df.loc[df["rest_days"].notna(), "rest_days"] = df.loc[df["rest_days"].notna(), "rest_days"].clip(
            lower=0, upper=30
        )

    if include_home_split:
        # prior same-split win rate with shift inside home/away subsets, then map back
        df["pre_home_win_pct"] = np.nan
        df["pre_away_win_pct"] = np.nan
        for team, idx in df.groupby("team").groups.items():
            sub = df.loc[idx].sort_values(["season", "week", "gameday", "game_id"])
            for home_val, col in ((1, "pre_home_win_pct"), (0, "pre_away_win_pct")):
                mask = sub["is_home"].astype(int) == home_val
                split = sub.loc[mask, "won"].astype(float)
                # shift+expanding only on this split's timeline
                rate = split.shift(1).expanding().mean()
                df.loc[rate.index, col] = rate
            # fill non-split rows with last known split rate (still pre-game via shift)
            df.loc[sub.index, "pre_home_win_pct"] = df.loc[sub.index, "pre_home_win_pct"].ffill()
            df.loc[sub.index, "pre_away_win_pct"] = df.loc[sub.index, "pre_away_win_pct"].ffill()

    if include_calendar:
        if "week" in df.columns:
            df["season_week"] = pd.to_numeric(df["week"], errors="coerce")
        if "gameday" in df.columns:
            gd = pd.to_datetime(df["gameday"], errors="coerce")
            df["month"] = gd.dt.month

    opp_src = [
        "game_id",
        "team",
        "pre_win_pct",
        "pre_avg_diff",
        "pre_games_played",
        "roll3_win_pct",
        "roll3_diff",
        "roll5_win_pct",
        "roll5_diff",
        "ewma5_win",
        "ewma5_diff",
        "roll5_pf",
        "roll5_pa",
    ]
    if "rest_days" in df.columns:
        opp_src.append("rest_days")
    if "pre_home_win_pct" in df.columns:
        opp_src.extend(["pre_home_win_pct", "pre_away_win_pct"])
    opp_src = [c for c in opp_src if c in df.columns]

    rename = {"team": "opponent"}
    for c in opp_src:
        if c in {"game_id", "team"}:
            continue
        rename[c] = f"opp_{c}"
    opp = df[opp_src].rename(columns=rename)
    df = df.merge(opp, on=["game_id", "opponent"], how="left")

    df["feature_win_pct_diff"] = df["pre_win_pct"] - df["opp_pre_win_pct"]
    df["feature_diff_diff"] = df["pre_avg_diff"] - df["opp_pre_avg_diff"]
    df["feature_roll3_win_diff"] = df["roll3_win_pct"] - df["opp_roll3_win_pct"]
    df["feature_roll5_diff_diff"] = df["roll5_diff"] - df["opp_roll5_diff"]
    if "ewma5_win" in df.columns and "opp_ewma5_win" in df.columns:
        df["feature_ewma5_win_diff"] = df["ewma5_win"] - df["opp_ewma5_win"]
    if "ewma5_diff" in df.columns and "opp_ewma5_diff" in df.columns:
        df["feature_ewma5_diff_diff"] = df["ewma5_diff"] - df["opp_ewma5_diff"]
    if "roll5_pf" in df.columns and "opp_roll5_pa" in df.columns:
        df["feature_pf_vs_opp_pa"] = df["roll5_pf"] - df["opp_roll5_pa"]
    if "rest_days" in df.columns and "opp_rest_days" in df.columns:
        df["feature_rest_diff"] = df["rest_days"] - df["opp_rest_days"]

    return df


# Original compact feature set (kept for back-compat pipelines)
DEFAULT_WIN_FEATURE_COLS = [
    "is_home",
    "feature_win_pct_diff",
    "feature_diff_diff",
    "feature_roll3_win_diff",
    "feature_roll5_diff_diff",
    "pre_games_played",
    "opp_pre_games_played",
]

# Richer default feature set for upgraded win models
RICH_WIN_FEATURE_COLS = [
    "is_home",
    "feature_win_pct_diff",
    "feature_diff_diff",
    "feature_roll3_win_diff",
    "feature_roll5_diff_diff",
    "feature_ewma5_win_diff",
    "feature_ewma5_diff_diff",
    "feature_pf_vs_opp_pa",
    "feature_rest_diff",
    "pre_games_played",
    "opp_pre_games_played",
    "season_week",
]
