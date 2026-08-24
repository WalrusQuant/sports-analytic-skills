#!/usr/bin/env python3
"""Build pre-event Elo ratings from a user-owned one-row-per-game table."""

from __future__ import annotations

import argparse
import math
import tempfile
from collections import defaultdict
from pathlib import Path


def load_table(path: Path):
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit("This command requires pandas. Install it with: pip install pandas") from exc
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if path.suffix.lower() in {".json", ".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=path.suffix.lower() != ".json")
    raise SystemExit("--input must be CSV, Parquet, JSON, JSONL, or NDJSON")


def ordering_key(series, label: str):
    import pandas as pd

    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().all():
        if not numeric.map(lambda value: math.isfinite(float(value))).all():
            raise SystemExit(f"{label!r} contains non-finite ordering values")
        return numeric
    chronological = pd.to_datetime(series, errors="coerce", utc=True, format="mixed")
    if chronological.isna().any():
        raise SystemExit(f"{label!r} must contain numeric or parseable chronological values")
    return chronological


def build_elo_table(
    games,
    *,
    season_col: str = "season",
    order_col: str = "game_date",
    game_col: str = "game_id",
    home_team_col: str = "home_team",
    away_team_col: str = "away_team",
    home_score_col: str = "home_score",
    away_score_col: str = "away_score",
    k: float = 20.0,
    home_adv: float = 65.0,
    init: float = 1500.0,
    carryover: float = 1.0,
):
    import numpy as np
    import pandas as pd

    columns = [
        season_col,
        order_col,
        game_col,
        home_team_col,
        away_team_col,
        home_score_col,
        away_score_col,
    ]
    missing = [column for column in columns if column not in games.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    if not math.isfinite(k) or k <= 0:
        raise SystemExit("--k must be a finite number greater than 0")
    if not math.isfinite(home_adv):
        raise SystemExit("--home-adv must be finite")
    if not math.isfinite(init):
        raise SystemExit("--init must be finite")
    if not math.isfinite(carryover) or not 0 <= carryover <= 1:
        raise SystemExit("--carryover must be between 0 and 1")

    complete = games.dropna(subset=columns).copy()
    if complete.empty:
        raise SystemExit("no complete games to rate")
    if complete[game_col].duplicated().any():
        raise SystemExit(f"{game_col} must be unique (one input row per game)")
    try:
        complete[home_score_col] = complete[home_score_col].astype(float)
        complete[away_score_col] = complete[away_score_col].astype(float)
    except (TypeError, ValueError) as exc:
        raise SystemExit("score columns must be numeric") from exc
    if not np.isfinite(complete[[home_score_col, away_score_col]].to_numpy()).all():
        raise SystemExit("score columns must contain only finite values")
    if (complete[home_team_col] == complete[away_team_col]).any():
        raise SystemExit("home and away team must differ on every row")

    complete["_season_order"] = ordering_key(complete[season_col], season_col)
    complete["_event_order"] = ordering_key(complete[order_col], order_col)
    complete = complete.sort_values(
        ["_season_order", "_event_order", game_col], kind="stable"
    )
    appearances = pd.concat(
        [
            complete[["_season_order", "_event_order", home_team_col]].rename(
                columns={home_team_col: "team"}
            ),
            complete[["_season_order", "_event_order", away_team_col]].rename(
                columns={away_team_col: "team"}
            ),
        ],
        ignore_index=True,
    )
    if appearances.duplicated(["_season_order", "_event_order", "team"]).any():
        raise SystemExit(
            f"{order_col!r} does not strictly order every team's games; "
            "provide a finer kickoff timestamp or event sequence"
        )

    ratings = defaultdict(lambda: init)
    current_season_order = None
    rows = []
    for _, game in complete.iterrows():
        season_order = game["_season_order"]
        if (
            current_season_order is not None
            and season_order != current_season_order
            and carryover < 1
        ):
            for team in list(ratings):
                ratings[team] = init + carryover * (ratings[team] - init)
        current_season_order = season_order
        home_team, away_team = game[home_team_col], game[away_team_col]
        home_pre, away_pre = ratings[home_team], ratings[away_team]
        home_elo_diff = (home_pre + home_adv) - away_pre
        home_probability = 1 / (1 + 10 ** (-home_elo_diff / 400))
        home_score = float(game[home_score_col])
        away_score = float(game[away_score_col])
        actual_home = 1.0 if home_score > away_score else (0.0 if home_score < away_score else 0.5)
        common = {
            season_col: game[season_col],
            order_col: game[order_col],
            game_col: game[game_col],
        }
        rows.extend(
            [
                {
                    **common,
                    "team": home_team,
                    "opponent": away_team,
                    "is_home": 1,
                    "elo_pre": home_pre,
                    "opponent_elo_pre": away_pre,
                    "rating_diff": home_pre - away_pre,
                    "elo_diff": home_elo_diff,
                    "home_advantage": home_adv,
                    "win_probability": home_probability,
                    "actual": actual_home,
                },
                {
                    **common,
                    "team": away_team,
                    "opponent": home_team,
                    "is_home": 0,
                    "elo_pre": away_pre,
                    "opponent_elo_pre": home_pre,
                    "rating_diff": away_pre - home_pre,
                    "elo_diff": -home_elo_diff,
                    "home_advantage": -home_adv,
                    "win_probability": 1 - home_probability,
                    "actual": 1 - actual_home,
                },
            ]
        )
        change = k * (actual_home - home_probability)
        ratings[home_team] += change
        ratings[away_team] -= change
    return pd.DataFrame(rows)


def write_csv_atomic(frame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            frame.to_csv(handle, index=False)
        temporary.replace(path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="CSV, Parquet, or JSON with one row per completed game")
    parser.add_argument("--out", type=Path, required=True, help="destination .csv with two as-of team rows per game")
    parser.add_argument("--season-col", default="season")
    parser.add_argument("--order-col", default="game_date", help="timestamp or numeric event-order column")
    parser.add_argument("--game-col", default="game_id")
    parser.add_argument("--home-team-col", default="home_team")
    parser.add_argument("--away-team-col", default="away_team")
    parser.add_argument("--home-score-col", default="home_score")
    parser.add_argument("--away-score-col", default="away_score")
    parser.add_argument("--k", type=float, default=20.0)
    parser.add_argument("--home-adv", type=float, default=65.0)
    parser.add_argument("--init", type=float, default=1500.0)
    parser.add_argument("--carryover", type=float, default=1.0, help="fraction of rating deviation carried into a new season")
    parser.add_argument("--force", action="store_true", help="replace an existing output file")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"--input does not exist: {args.input}")
    if args.out.suffix.lower() != ".csv":
        parser.error("--out must end in .csv")
    if args.input.resolve() == args.out.resolve():
        parser.error("--out must differ from --input")
    if args.out.exists() and not args.force:
        parser.error("--out already exists; pass --force to replace it")

    games = load_table(args.input)
    output = build_elo_table(
        games,
        season_col=args.season_col,
        order_col=args.order_col,
        game_col=args.game_col,
        home_team_col=args.home_team_col,
        away_team_col=args.away_team_col,
        home_score_col=args.home_score_col,
        away_score_col=args.away_score_col,
        k=args.k,
        home_adv=args.home_adv,
        init=args.init,
        carryover=args.carryover,
    )
    write_csv_atomic(output, args.out)
    print(f"rows={len(output)} teams={output['team'].nunique()} wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
