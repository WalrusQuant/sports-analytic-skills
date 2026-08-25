#!/usr/bin/env python3
"""Monte Carlo win counts across supplied one-row-per-game schedule rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_table(path: Path):
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit(
            "pandas is required; install it with: python -m pip install pandas"
        ) from exc
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if suffix in {".json", ".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=suffix != ".json")
    raise SystemExit("--input must be CSV, Parquet, JSON, JSONL, or NDJSON")


def simulate_season(
    games: Any,
    *,
    probability_col: str,
    n_sims: int,
    seed: int,
    threshold: float | None,
) -> dict[str, Any]:
    import numpy as np

    required = {"team", "opponent", probability_col}
    missing = sorted(required.difference(games.columns))
    if missing:
        raise ValueError(f"input is missing required columns: {', '.join(missing)}")
    if n_sims < 1:
        raise ValueError("n_sims must be at least 1")
    if games.empty:
        raise ValueError("input contains no games")
    if games[["team", "opponent", probability_col]].isna().any().any():
        raise ValueError("team, opponent, and probability must not be null")
    if (games["team"] == games["opponent"]).any():
        raise ValueError("team and opponent must differ")

    try:
        probabilities = games[probability_col].to_numpy(dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{probability_col} must be numeric") from exc
    if not np.isfinite(probabilities).all() or not (
        (probabilities >= 0) & (probabilities <= 1)
    ).all():
        raise ValueError(f"{probability_col} must contain finite values in [0, 1]")

    rng = np.random.default_rng(seed)
    teams = sorted(set(games["team"]).union(set(games["opponent"])))
    team_index = {team: index for index, team in enumerate(teams)}
    home_idx = games["team"].map(team_index).to_numpy()
    away_idx = games["opponent"].map(team_index).to_numpy()
    wins = np.zeros((n_sims, len(teams)), dtype=float)

    for game_index, probability in enumerate(probabilities):
        home_wins = rng.random(n_sims) < probability
        wins[:, home_idx[game_index]] += home_wins
        wins[:, away_idx[game_index]] += ~home_wins

    schedule_win_summaries = []
    for team in teams:
        values = wins[:, team_index[team]]
        row = {
            "team": team,
            "mean_wins_in_supplied_games": float(values.mean()),
            "p05_wins_in_supplied_games": float(np.quantile(values, 0.05)),
            "p50_wins_in_supplied_games": float(np.quantile(values, 0.50)),
            "p95_wins_in_supplied_games": float(np.quantile(values, 0.95)),
        }
        if threshold is not None:
            row["prob_wins_in_supplied_games_at_least_threshold"] = float(
                (values >= threshold).mean()
            )
        row["mean_wins"] = row["mean_wins_in_supplied_games"]
        row["p05"] = row["p05_wins_in_supplied_games"]
        row["p50"] = row["p50_wins_in_supplied_games"]
        row["p95"] = row["p95_wins_in_supplied_games"]
        if threshold is not None:
            row["prob_wins_at_least_threshold"] = row[
                "prob_wins_in_supplied_games_at_least_threshold"
            ]
        schedule_win_summaries.append(row)

    ordered_summaries = sorted(
        schedule_win_summaries,
        key=lambda row: row["mean_wins_in_supplied_games"],
        reverse=True,
    )

    return {
        "n_sims": n_sims,
        "seed": seed,
        "n_games": len(games),
        "n_teams": len(teams),
        "probability_column": probability_col,
        "win_threshold": threshold,
        "win_count_scope": "wins in supplied game rows after CLI filters",
        "includes_completed_wins_outside_supplied_rows": False,
        "is_full_season_total": False,
        "scope_note": (
            "These counts are full-season totals only when the supplied rows cover "
            "every game in the season; the helper does not add prior completed wins."
        ),
        "assumptions": [
            "independent games conditional on supplied pre-event probabilities",
            "one row per game",
            "the focal team wins with the supplied probability",
        ],
        "schedule_win_summaries": ordered_summaries,
        "standings": ordered_summaries,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, required=True, help="CSV, Parquet, or JSON schedule"
    )
    parser.add_argument("--season", required=True, help="Season value to simulate")
    parser.add_argument("--season-col", default="season")
    parser.add_argument("--game-col", default="game_id")
    parser.add_argument("--home-col", default="is_home")
    parser.add_argument("--team-col", default="team")
    parser.add_argument("--opponent-col", default="opponent")
    parser.add_argument("--probability-col", default="win_probability")
    parser.add_argument("--n-sims", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument(
        "--threshold",
        type=float,
        help="Optional threshold for wins across the supplied game rows",
    )
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.n_sims < 1:
        raise SystemExit("--n-sims must be at least 1")
    if args.threshold is not None and args.threshold < 0:
        raise SystemExit("--threshold must not be negative")
    if args.input.resolve() == args.out.resolve():
        raise SystemExit("--out must differ from --input")
    frame = load_table(args.input)
    required = [
        args.season_col,
        args.game_col,
        args.home_col,
        args.team_col,
        args.opponent_col,
        args.probability_col,
    ]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")

    import pandas as pd

    home = pd.to_numeric(frame[args.home_col], errors="coerce")
    invalid_home = frame[args.home_col].notna() & home.isna()
    if home.isna().any() or invalid_home.any() or not set(home.unique()) <= {0, 1}:
        raise SystemExit(f"{args.home_col!r} must contain non-null 0/1 values")
    selected = frame[frame[args.season_col].astype(str) == str(args.season)].copy()
    selected = selected[home.loc[selected.index] == 1].copy()
    if selected.empty:
        raise SystemExit(f"no one-row-per-game records for season {args.season!r}")
    if selected[args.game_col].isna().any() or selected[args.game_col].duplicated().any():
        raise SystemExit(
            f"{args.game_col!r} must be non-null and unique after season/home filtering"
        )
    selected = selected.rename(
        columns={
            args.team_col: "team",
            args.opponent_col: "opponent",
            args.probability_col: "win_probability",
        }
    )

    try:
        report = simulate_season(
            selected,
            probability_col="win_probability",
            n_sims=args.n_sims,
            seed=args.seed,
            threshold=args.threshold,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    report.update(
        {
            "season": args.season,
            "source": str(args.input),
            "game_column": args.game_col,
        }
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"season={args.season} games={report['n_games']} sims={args.n_sims}")
    print("win counts cover supplied game rows only; prior completed wins are not added")
    for row in report["schedule_win_summaries"][:5]:
        print(
            f"  {row['team']}: mean_supplied={row['mean_wins_in_supplied_games']:.1f} "
            f"p05_supplied={row['p05_wins_in_supplied_games']:.0f} "
            f"p95_supplied={row['p95_wins_in_supplied_games']:.0f}"
        )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
