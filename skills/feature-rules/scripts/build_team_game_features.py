#!/usr/bin/env python3
"""Build shifted pre-game form features from a doubled team-game panel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REQUIRED_CORE = (
    "game_id",
    "team",
    "opponent",
    "is_home",
    "won",
    "point_diff",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV, Parquet, or JSON team-game panel")
    parser.add_argument("--out", required=True, help="Output CSV/Parquet/JSON feature table")
    parser.add_argument("--game-col", default="game_id")
    parser.add_argument("--team-col", default="team")
    parser.add_argument("--opponent-col", default="opponent")
    parser.add_argument("--home-col", default="is_home")
    parser.add_argument("--outcome-col", default="won")
    parser.add_argument("--margin-col", default="point_diff")
    parser.add_argument(
        "--time-col",
        default="gameday",
        help="Sortable event time/date column (default: gameday)",
    )
    parser.add_argument(
        "--order-col",
        default="",
        help="Optional strict sequence used when time values can tie",
    )
    parser.add_argument(
        "--split-col",
        default="season",
        help="Optional season/group column to carry through (default: season if present)",
    )
    parser.add_argument(
        "--min-prior-games",
        type=int,
        default=0,
        help="Drop rows where either side has fewer than this many prior games",
    )
    parser.add_argument(
        "--manifest-out",
        default="",
        help="Optional JSON path describing generated features and legality notes",
    )
    return parser.parse_args()


def load_frame(path: str):
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit(
            "pandas is required; install it with: python -m pip install pandas"
        ) from exc
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if suffix in {".json", ".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=suffix != ".json")
    raise SystemExit("--input must be CSV, Parquet, JSON, JSONL, or NDJSON")


def write_frame(frame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        frame.to_csv(path, index=False)
    elif suffix in {".parquet", ".pq"}:
        frame.to_parquet(path, index=False)
    elif suffix == ".json":
        frame.to_json(path, orient="records", indent=2)
    else:
        raise SystemExit("--out must end in .csv, .parquet, .pq, or .json")


def normalized_order_values(series, column: str):
    import numpy as np
    import pandas as pd

    if series.isna().any():
        raise SystemExit(f"{column!r} must not contain null values")
    if pd.api.types.is_bool_dtype(series.dtype):
        raise SystemExit(f"{column!r} must not use boolean values")
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().all():
        values = numeric.to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise SystemExit(f"{column!r} must contain finite ordering values")
        return pd.Series(values, index=series.index)
    timestamps = pd.to_datetime(series, errors="coerce", utc=True, format="mixed")
    if timestamps.isna().any():
        raise SystemExit(f"{column!r} must contain numeric or parseable timestamp values")
    return pd.Series(timestamps.astype("int64"), index=series.index)


def build_features(
    frame,
    *,
    game_col: str,
    team_col: str,
    opponent_col: str,
    home_col: str,
    outcome_col: str,
    margin_col: str,
    time_col: str,
    order_col: str | None,
    split_col: str | None,
    min_prior_games: int,
):
    import pandas as pd

    required = [game_col, team_col, opponent_col, home_col, outcome_col, margin_col, time_col]
    if order_col:
        required.append(order_col)
    if split_col:
        required.append(split_col)
    missing = [c for c in required if c not in frame.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")

    out = frame.copy()
    out[home_col] = pd.to_numeric(out[home_col], errors="coerce")
    out[outcome_col] = pd.to_numeric(out[outcome_col], errors="coerce")
    out[margin_col] = pd.to_numeric(out[margin_col], errors="coerce")
    if out[home_col].isna().any() or not set(out[home_col].dropna().unique()) <= {0, 1}:
        raise SystemExit(f"{home_col!r} must be binary 0/1")
    if out[outcome_col].isna().any() or not set(out[outcome_col].dropna().unique()) <= {0, 1}:
        raise SystemExit(f"{outcome_col!r} must be binary 0/1 with no nulls")
    if out[margin_col].isna().any():
        raise SystemExit(f"{margin_col!r} must not contain nulls")

    # Basic grain checks for a doubled team-game panel.
    rows_per_game = out.groupby(game_col).size()
    bad_counts = rows_per_game[rows_per_game != 2]
    if len(bad_counts):
        raise SystemExit(
            f"{game_col!r} must have exactly 2 rows per game; "
            f"found {len(bad_counts)} games with other counts"
        )
    if out.duplicated([game_col, team_col]).any():
        raise SystemExit(f"duplicate ({game_col}, {team_col}) keys present")

    sort_key = "__feature_sort_key"
    while sort_key in out.columns:
        sort_key += "_"
    order_name = order_col or time_col
    out[sort_key] = normalized_order_values(out[order_name], order_name)
    out = out.sort_values([team_col, sort_key, game_col], kind="stable").copy()

    grouped = out.groupby(team_col, sort=False, group_keys=False)
    out["pre_games_played"] = grouped.cumcount()
    out["pre_win_pct"] = grouped[outcome_col].transform(
        lambda s: s.shift(1).expanding(min_periods=1).mean()
    )
    out["pre_avg_diff"] = grouped[margin_col].transform(
        lambda s: s.shift(1).expanding(min_periods=1).mean()
    )
    # Rest days when time is parseable as datetime; else leave null.
    times = pd.to_datetime(out[time_col], errors="coerce", utc=True, format="mixed")
    if times.notna().all():
        prior_time = times.groupby(out[team_col], sort=False).shift(1)
        out["rest_days"] = (times - prior_time).dt.total_seconds() / 86400.0
    else:
        out["rest_days"] = pd.NA

    opp = out[
        [game_col, team_col, "pre_win_pct", "pre_avg_diff", "pre_games_played", "rest_days"]
    ].rename(
        columns={
            team_col: opponent_col,
            "pre_win_pct": "opp_pre_win_pct",
            "pre_avg_diff": "opp_pre_avg_diff",
            "pre_games_played": "opp_pre_games_played",
            "rest_days": "opp_rest_days",
        }
    )
    out = out.merge(opp, on=[game_col, opponent_col], how="left", validate="one_to_one")
    out["feature_win_pct_diff"] = out["pre_win_pct"] - out["opp_pre_win_pct"]
    out["feature_diff_diff"] = out["pre_avg_diff"] - out["opp_pre_avg_diff"]
    out["feature_rest_diff"] = out["rest_days"] - out["opp_rest_days"]
    out[home_col] = out[home_col].astype(int)
    out[outcome_col] = out[outcome_col].astype(int)

    if min_prior_games > 0:
        out = out.loc[
            out["pre_games_played"].ge(min_prior_games)
            & out["opp_pre_games_played"].ge(min_prior_games)
        ].copy()

    keep = [
        c
        for c in [
            split_col,
            game_col,
            time_col,
            order_col,
            team_col,
            opponent_col,
            home_col,
            outcome_col,
            margin_col,
            "pre_games_played",
            "opp_pre_games_played",
            "pre_win_pct",
            "opp_pre_win_pct",
            "pre_avg_diff",
            "opp_pre_avg_diff",
            "rest_days",
            "opp_rest_days",
            "feature_win_pct_diff",
            "feature_diff_diff",
            "feature_rest_diff",
        ]
        if c and c in out.columns
    ]
    # Preserve additional user columns that are not targets of transforms.
    extras = [c for c in frame.columns if c not in keep and c not in REQUIRED_CORE]
    # Don't auto-pass unknown extras that could be post-event; keep only split/week-like ids.
    safe_extras = [c for c in extras if c in frame.columns and c.lower() in {"week", "season_type", "season"}]
    final_cols = list(dict.fromkeys([*keep, *safe_extras]))
    result = out[final_cols].reset_index(drop=True)
    return result


def main() -> int:
    args = parse_args()
    if args.min_prior_games < 0:
        raise SystemExit("--min-prior-games must be >= 0")

    input_path = Path(args.input).resolve()
    out_path = Path(args.out).resolve()
    if input_path == out_path:
        raise SystemExit("--input and --out must be different files")

    frame = load_frame(str(input_path))
    split_col = args.split_col if args.split_col and args.split_col in frame.columns else (
        "season" if "season" in frame.columns else None
    )
    if args.split_col and args.split_col not in frame.columns and args.split_col != "season":
        raise SystemExit(f"split column {args.split_col!r} not found")

    order_col = args.order_col or None
    if order_col == "":
        order_col = None

    result = build_features(
        frame,
        game_col=args.game_col,
        team_col=args.team_col,
        opponent_col=args.opponent_col,
        home_col=args.home_col,
        outcome_col=args.outcome_col,
        margin_col=args.margin_col,
        time_col=args.time_col,
        order_col=order_col,
        split_col=split_col,
        min_prior_games=args.min_prior_games,
    )
    write_frame(result, out_path)

    feature_cols = [
        args.home_col,
        "feature_win_pct_diff",
        "feature_diff_diff",
        "feature_rest_diff",
    ]
    present_features = [c for c in feature_cols if c in result.columns]
    manifest = {
        "artifact_type": "team_game_pregame_features",
        "source": str(input_path),
        "output": str(out_path),
        "grain": "team-game",
        "decision_time": "pre-event / kickoff-style",
        "rows_in": int(len(frame)),
        "rows_out": int(len(result)),
        "min_prior_games": args.min_prior_games,
        "modeling_feature_defaults": present_features,
        "generated_columns": {
            "pre_win_pct": "shifted expanding mean of prior won",
            "pre_avg_diff": "shifted expanding mean of prior point_diff",
            "pre_games_played": "count of prior entity games",
            "rest_days": "days since prior entity game when time is parseable",
            "feature_win_pct_diff": "pre_win_pct - opponent pre_win_pct",
            "feature_diff_diff": "pre_avg_diff - opponent pre_avg_diff",
            "feature_rest_diff": "rest_days - opponent rest_days",
        },
        "legality_notes": [
            "All form features use shift(1) before aggregation.",
            "Opponent features come from the opponent's own pre-event row joined on game_id.",
            "Current-event outcomes are retained as labels only; do not use them as predictors.",
            "Automated construction does not replace leakage-audit.",
        ],
        "next_skills": [
            "leakage-audit",
            "validation-design",
            "baseline-models",
        ],
    }
    print(json.dumps({"rows_out": manifest["rows_out"], "features": present_features}, indent=2))
    print(f"wrote {out_path}", file=sys.stderr)
    if args.manifest_out:
        man_path = Path(args.manifest_out)
        man_path.parent.mkdir(parents=True, exist_ok=True)
        man_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {man_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
