#!/usr/bin/env python3
"""Build as-of Elo ratings for an NFL team-game panel via sports_ds.ratings."""

from __future__ import annotations

import argparse
from pathlib import Path

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.ratings.elo import build_elo_asof_table


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


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
