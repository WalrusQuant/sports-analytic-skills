#!/usr/bin/env python3
"""Walk-forward error slices for sports_ds logistic win model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.models.baselines import fit_logistic_baseline
from sports_ds.pipelines.nfl_win_model import FEATURE_COLS
from sports_ds.validation.splits import season_walk_forward_masks


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def _ll(y, p, eps=1e-15):
    p = np.clip(np.asarray(p, dtype=float), eps, 1 - eps)
    y = np.asarray(y, dtype=float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seasons", default="2018-2024")
    ap.add_argument("--out", default="data/slice_errors.json")
    args = ap.parse_args()

    df = add_pregame_form_features(load_team_game_panel(_parse_seasons(args.seasons)))
    df = df.dropna(subset=FEATURE_COLS + ["won"]).copy()
    df = df[(df.pre_games_played >= 3) & (df.opp_pre_games_played >= 3)]

    rows = []
    for season, tr, te in season_walk_forward_masks(df):
        _, res, pred = fit_logistic_baseline(df, FEATURE_COLS, tr, te)
        part = df.loc[te, ["won", "is_home", "season", "week"]].copy()
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
        rows.append(
            {
                "season": int(season),
                "slice": "all",
                "n": int(te.sum()),
                "log_loss": float(res.log_loss),
                "accuracy": float(res.accuracy),
                "base_rate": float(part["won"].mean()),
            }
        )

    report = {"model": "logistic_baseline", "slices": rows}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(pd.DataFrame(rows).to_string(index=False))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
