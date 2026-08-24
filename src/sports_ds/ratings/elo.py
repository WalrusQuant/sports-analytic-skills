"""As-of Elo ratings for team-game panels."""

from __future__ import annotations

import numpy as np
import pandas as pd


def expected_score(rating: float, opp_rating: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((opp_rating - rating) / 400.0))


def margin_multiplier(point_diff: float) -> float:
    md = abs(float(point_diff))
    return float(np.log(max(md, 1.0) + 1.0))


def build_elo_asof_table(
    panel: pd.DataFrame,
    k: float = 20.0,
    home_adv: float = 65.0,
    init: float = 1500.0,
    use_margin: bool = True,
) -> pd.DataFrame:
    """Return team-game rows with pre-game Elo fields only (no look-ahead).

    Expects team-game panel columns:
    game_id, season, week, team, opponent, is_home, won, point_diff
    optional: gameday
    """
    required = ["game_id", "season", "week", "team", "opponent", "is_home", "won", "point_diff"]
    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"panel missing columns: {missing}")

    df = panel.copy()
    sort_cols = [c for c in ["gameday", "season", "week", "game_id"] if c in df.columns]
    home = df[df["is_home"] == 1].sort_values(sort_cols).copy()

    ratings: dict[str, float] = {}
    rows: list[dict] = []

    for r in home.itertuples(index=False):
        home_team = r.team
        away_team = r.opponent
        rh = ratings.get(home_team, init)
        ra = ratings.get(away_team, init)

        exp_home = expected_score(rh + home_adv, ra)
        exp_away = 1.0 - exp_home
        score_home = float(r.won)
        score_away = 1.0 - score_home
        mult = margin_multiplier(r.point_diff) if use_margin else 1.0
        delta_home = k * mult * (score_home - exp_home)
        delta_away = k * mult * (score_away - exp_away)

        rows.append(
            {
                "game_id": r.game_id,
                "season": int(r.season),
                "week": int(r.week),
                "team": home_team,
                "opponent": away_team,
                "is_home": 1,
                "won": int(r.won),
                "point_diff": float(r.point_diff),
                "elo_pre": rh,
                "opp_elo_pre": ra,
                "elo_diff": (rh + home_adv) - ra,
                "elo_expected": exp_home,
            }
        )
        rows.append(
            {
                "game_id": r.game_id,
                "season": int(r.season),
                "week": int(r.week),
                "team": away_team,
                "opponent": home_team,
                "is_home": 0,
                "won": 1 - int(r.won),
                "point_diff": -float(r.point_diff),
                "elo_pre": ra,
                "opp_elo_pre": rh,
                "elo_diff": ra - (rh + home_adv),
                "elo_expected": exp_away,
            }
        )

        # update only after storing pre-game ratings
        ratings[home_team] = rh + delta_home
        ratings[away_team] = ra + delta_away

    out = pd.DataFrame(rows)
    return out.sort_values(
        ["season", "week", "game_id", "is_home"],
        ascending=[True, True, True, False],
    ).reset_index(drop=True)


def add_elo_asof(
    panel: pd.DataFrame,
    k: float = 20.0,
    home_adv: float = 65.0,
    init: float = 1500.0,
    use_margin: bool = True,
) -> pd.DataFrame:
    """Merge pre-game Elo fields onto a full team-game panel."""
    elo = build_elo_asof_table(
        panel, k=k, home_adv=home_adv, init=init, use_margin=use_margin
    )
    keep = ["game_id", "team", "elo_pre", "opp_elo_pre", "elo_diff", "elo_expected"]
    return panel.merge(elo[keep], on=["game_id", "team"], how="left")
