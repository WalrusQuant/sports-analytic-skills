#!/usr/bin/env python3
"""Monte Carlo season win totals from an Elo as-of table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def elo_diff_to_prob(elo_diff: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + 10.0 ** (-np.asarray(elo_diff, dtype=float) / 400.0))


def simulate_season(home_games: pd.DataFrame, n_sims: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    teams = sorted(set(home_games["team"]).union(set(home_games["opponent"])))
    team_index = {t: i for i, t in enumerate(teams)}
    n_teams = len(teams)
    n_games = len(home_games)

    p_home = elo_diff_to_prob(home_games["elo_diff"].to_numpy())
    home_idx = home_games["team"].map(team_index).to_numpy()
    away_idx = home_games["opponent"].map(team_index).to_numpy()

    wins = np.zeros((n_sims, n_teams), dtype=float)
    # vectorized by game chunks to limit memory
    for g in range(n_games):
        draws = rng.random(n_sims) < p_home[g]
        wins[:, home_idx[g]] += draws.astype(float)
        wins[:, away_idx[g]] += (~draws).astype(float)

    summary = []
    for t in teams:
        w = wins[:, team_index[t]]
        summary.append(
            {
                "team": t,
                "mean_wins": float(w.mean()),
                "p05": float(np.quantile(w, 0.05)),
                "p50": float(np.quantile(w, 0.50)),
                "p95": float(np.quantile(w, 0.95)),
            }
        )
    summary = sorted(summary, key=lambda r: r["mean_wins"], reverse=True)
    return {
        "n_sims": n_sims,
        "seed": seed,
        "n_games": n_games,
        "n_teams": n_teams,
        "assumptions": [
            "independent games conditional on pre-game Elo probs",
            "probs from elo_diff via logistic Elo formula",
            "home rows only (each game once)",
        ],
        "standings": summary,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--elo-csv", required=True)
    ap.add_argument("--season", type=int, required=True)
    ap.add_argument("--n-sims", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default="data/season_win_sim.json")
    args = ap.parse_args()

    elo = pd.read_csv(args.elo_csv)
    season = elo[elo["season"] == args.season].copy()
    home = season[season["is_home"] == 1].copy()
    if home.empty:
        raise SystemExit(f"no home games for season {args.season}")

    report = simulate_season(home, n_sims=args.n_sims, seed=args.seed)
    report["season"] = args.season
    report["source_csv"] = args.elo_csv

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"season={args.season} games={report['n_games']} sims={args.n_sims}")
    for row in report["standings"][:5]:
        print(f"  {row['team']}: mean={row['mean_wins']:.1f} p05={row['p05']:.0f} p95={row['p95']:.0f}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
