#!/usr/bin/env python3
"""Walk-forward error slices for sports_ds logistic win models."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.models.baselines import fit_logistic_baseline
from sports_ds.pipelines.team_win import FEATURE_COLS
from sports_ds.validation.splits import season_walk_forward_masks


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def _load_panel(sport: str, seasons: list[int]) -> pd.DataFrame:
    if sport == "nfl":
        from sports_ds.data.nfl import load_team_game_panel

        return load_team_game_panel(seasons)
    if sport == "nba":
        from sports_ds.data.nba import load_nba_team_game_panel

        return load_nba_team_game_panel(seasons)
    if sport == "mlb":
        from sports_ds.data.mlb import load_mlb_team_game_panel

        return load_mlb_team_game_panel(seasons)
    raise ValueError(sport)


def _ll(y, p, eps=1e-15):
    p = np.clip(np.asarray(p, dtype=float), eps, 1 - eps)
    y = np.asarray(y, dtype=float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sport", default="nfl", choices=["nfl", "nba", "mlb"])
    ap.add_argument("--seasons", default="2018-2024")
    ap.add_argument("--min-train-seasons", type=int, default=2)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    seasons = _parse_seasons(args.seasons)
    df = add_pregame_form_features(_load_panel(args.sport, seasons))
    df = df.dropna(subset=FEATURE_COLS + ["won"]).copy()
    df = df[(df.pre_games_played >= 3) & (df.opp_pre_games_played >= 3)]

    rows = []
    for season, tr, te in season_walk_forward_masks(df, min_train_seasons=args.min_train_seasons):
        _, res, pred = fit_logistic_baseline(df, FEATURE_COLS, tr, te)
        part = df.loc[te].dropna(subset=FEATURE_COLS + ["won"]).copy()
        part["p"] = np.asarray(pred, dtype=float)
        for home_val, name in [(1, "home"), (0, "away")]:
            sub = part[part["is_home"] == home_val]
            if sub.empty:
                continue
            y = sub["won"].to_numpy(dtype=float)
            p = sub["p"].to_numpy(dtype=float)
            rows.append(
                {
                    "season": int(season),
                    "slice": name,
                    "n": int(len(sub)),
                    "log_loss": _ll(y, p),
                    "accuracy": float(((p >= 0.5) == y).mean()),
                    "base_rate": float(y.mean()),
                }
            )
        # probability tails
        for lo, hi, name in [(0.0, 0.35, "p_low"), (0.35, 0.65, "p_mid"), (0.65, 1.01, "p_high")]:
            sub = part[(part["p"] >= lo) & (part["p"] < hi)]
            if len(sub) < 20:
                continue
            y = sub["won"].to_numpy(dtype=float)
            p = sub["p"].to_numpy(dtype=float)
            rows.append(
                {
                    "season": int(season),
                    "slice": name,
                    "n": int(len(sub)),
                    "log_loss": _ll(y, p),
                    "accuracy": float(((p >= 0.5) == y).mean()),
                    "base_rate": float(y.mean()),
                    "mean_p": float(p.mean()),
                }
            )
        rows.append(
            {
                "season": int(season),
                "slice": "all",
                "n": int(len(part)),
                "log_loss": float(res.log_loss),
                "accuracy": float(res.accuracy),
                "base_rate": float(part["won"].mean()),
            }
        )

    report = {"sport": args.sport, "model": "logistic_form", "slices": rows}
    out = Path(args.out or f"data/{args.sport}_slice_errors.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(pd.DataFrame(rows).to_string(index=False))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
