#!/usr/bin/env python3
"""Build as-of Elo ratings for an NFL team-game panel."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from sports_ds.data.nfl import load_team_game_panel


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def expected_score(rating: float, opp_rating: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((opp_rating - rating) / 400.0))


def margin_multiplier(point_diff: float) -> float:
    # fiveThirtyEight-style diminishing returns-ish
    md = abs(float(point_diff))
    return np.log(max(md, 1.0) + 1.0)


def build_elo_asof_table(
    panel: pd.DataFrame,
    k: float = 20.0,
    home_adv: float = 65.0,
    init: float = 1500.0,
    use_margin: bool = True,
) -> pd.DataFrame:
    """Return team-game rows with pre-game Elo fields.

    Expects sports_ds team-game panel with columns:
    game_id, season, week, team, opponent, is_home, won, point_diff, gameday(optional)
    """
    df = panel.copy()
    sort_cols = [c for c in ["gameday", "season", "week", "game_id"] if c in df.columns]
    # process each game once using home rows
    home = df[df["is_home"] == 1].sort_values(sort_cols).copy()

    ratings: dict[str, float] = {}
    rows = []

    for r in home.itertuples(index=False):
        home_team = r.team
        away_team = r.opponent
        rh = ratings.get(home_team, init)
        ra = ratings.get(away_team, init)

        # store pre ratings on home and away perspectives
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
                "season": r.season,
                "week": r.week,
                "team": home_team,
                "opponent": away_team,
                "is_home": 1,
                "won": int(r.won),
                "point_diff": float(r.point_diff),
                "elo_pre": rh,
                "opp_elo_pre": ra,
                "elo_diff": (rh + home_adv) - ra,
            }
        )
        rows.append(
            {
                "game_id": r.game_id,
                "season": r.season,
                "week": r.week,
                "team": away_team,
                "opponent": home_team,
                "is_home": 0,
                "won": 1 - int(r.won),
                "point_diff": -float(r.point_diff),
                "elo_pre": ra,
                "opp_elo_pre": rh,
                "elo_diff": ra - (rh + home_adv),
            }
        )

        ratings[home_team] = rh + delta_home
        ratings[away_team] = ra + delta_away

    out = pd.DataFrame(rows)
    return out.sort_values(["season", "week", "game_id", "is_home"], ascending=[True, True, True, False]).reset_index(drop=True)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seasons", default="2018-2024")
    p.add_argument("--k", type=float, default=20.0)
    p.add_argument("--home-adv", type=float, default=65.0)
    p.add_argument("--init", type=float, default=1500.0)
    p.add_argument("--out", default="data/elo_asof.csv")
    args = p.parse_args()

    panel = load_team_game_panel(_parse_seasons(args.seasons))
    elo = build_elo_asof_table(panel, k=args.k, home_adv=args.home_adv, init=args.init)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    elo.to_csv(out, index=False)
    print(f"rows={len(elo)} teams={elo.team.nunique()} wrote {out}")
    print(elo[["season", "week", "team", "opponent", "is_home", "elo_pre", "elo_diff", "won"]].head(6).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
