"""Time-safe pre-game player form features (multi-sport)."""

from __future__ import annotations

import pandas as pd


PLAYER_TARGET_DEFAULT = "fantasy_points_ppr"

# NFL defaults
NFL_STAT_COLS = [
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
NFL_POSITIONS = ("QB", "RB", "WR", "TE")
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

# NBA
NBA_STAT_COLS = [
    "fantasy_points",
    "points",
    "rebounds",
    "assists",
    "steals",
    "blocks",
    "turnovers",
    "minutes",
    "fga",
    "fg3a",
    "fta",
    "plus_minus",
]
NBA_POSITIONS = ("PG", "SG", "SF", "PF", "C", "G", "F")
DEFAULT_NBA_PLAYER_FEATURE_COLS = [
    "is_home",
    "season_week",
    "pre_games_played",
    "pre_fantasy_points",
    "roll3_fantasy_points",
    "roll5_fantasy_points",
    "ewma5_fantasy_points",
    "pre_points",
    "roll3_points",
    "roll5_points",
    "pre_rebounds",
    "roll3_rebounds",
    "pre_assists",
    "roll3_assists",
    "pre_minutes",
    "roll3_minutes",
    "pre_steals",
    "pre_blocks",
    "pre_turnovers",
    "pre_fga",
    "pre_fg3a",
    "pos_PG",
    "pos_SG",
    "pos_SF",
    "pos_PF",
    "pos_C",
    "pos_G",
    "pos_F",
]

# MLB batters
MLB_STAT_COLS = [
    "fantasy_points",
    "plate_appearances",
    "at_bats",
    "hits",
    "total_bases",
    "home_runs",
    "doubles",
    "triples",
    "walks",
    "strikeouts",
    "rbi",
    "runs",
    "stolen_bases",
]
MLB_POSITIONS = ("C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH", "OF", "TWP", "P")
DEFAULT_MLB_PLAYER_FEATURE_COLS = [
    "is_home",
    "season_week",
    "pre_games_played",
    "pre_fantasy_points",
    "roll3_fantasy_points",
    "roll5_fantasy_points",
    "ewma5_fantasy_points",
    "pre_plate_appearances",
    "roll3_plate_appearances",
    "pre_hits",
    "roll3_hits",
    "pre_total_bases",
    "roll3_total_bases",
    "pre_home_runs",
    "roll3_home_runs",
    "pre_walks",
    "roll3_walks",
    "pre_strikeouts",
    "roll3_strikeouts",
    "pre_rbi",
    "pre_runs",
    "pre_stolen_bases",
]


def add_pregame_player_form_features(
    panel: pd.DataFrame,
    *,
    windows: list[int] | None = None,
    ewma_spans: list[int] | None = None,
    stat_cols: list[str] | None = None,
    position_values: tuple[str, ...] | list[str] | None = None,
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
        # auto-detect common targets present on the panel
        candidates = list(
            dict.fromkeys(NFL_STAT_COLS + NBA_STAT_COLS + MLB_STAT_COLS + ["fantasy_points_ppr", "fantasy_points"])
        )
        stat_cols = [c for c in candidates if c in panel.columns]
    if position_values is None:
        if "position" in panel.columns:
            # infer from data + known sets
            vals = set(panel["position"].dropna().astype(str).unique())
            if vals & set(NFL_POSITIONS):
                position_values = NFL_POSITIONS
            elif vals & set(NBA_POSITIONS):
                position_values = NBA_POSITIONS
            elif vals & set(MLB_POSITIONS):
                position_values = MLB_POSITIONS
            else:
                position_values = tuple(sorted(vals))[:12]
        else:
            position_values = ()

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

    if "week" in df.columns:
        df["season_week"] = pd.to_numeric(df["week"], errors="coerce")

    if "position" in df.columns and position_values:
        for pos in position_values:
            safe = str(pos).replace(" ", "_")
            df[f"pos_{safe}"] = (df["position"].astype(str) == str(pos)).astype(int)

    return df
