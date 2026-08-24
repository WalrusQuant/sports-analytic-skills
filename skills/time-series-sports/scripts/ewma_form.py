#!/usr/bin/env python3
"""Build shifted EWMA form features on NFL team-game panel."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from sports_ds.data.nfl import load_team_game_panel


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def add_ewma_form(panel: pd.DataFrame, span: float = 5.0) -> pd.DataFrame:
    df = panel.sort_values(["team", "season", "week", "game_id"]).copy()
    g = df.groupby("team", group_keys=False)
    df["prior_won"] = g["won"].shift(1)
    df["prior_diff"] = g["point_diff"].shift(1)
    df["ewma_win"] = g["prior_won"].transform(lambda s: s.ewm(span=span, adjust=False).mean())
    df["ewma_diff"] = g["prior_diff"].transform(lambda s: s.ewm(span=span, adjust=False).mean())
    # opponent join
    opp = df[["game_id", "team", "ewma_win", "ewma_diff"]].rename(
        columns={"team": "opponent", "ewma_win": "opp_ewma_win", "ewma_diff": "opp_ewma_diff"}
    )
    out = df.merge(opp, on=["game_id", "opponent"], how="left")
    out["ewma_win_diff"] = out["ewma_win"] - out["opp_ewma_win"]
    out["ewma_diff_diff"] = out["ewma_diff"] - out["opp_ewma_diff"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seasons", default="2023-2024")
    ap.add_argument("--span", type=float, default=5.0)
    ap.add_argument("--out", default="data/ewma_form.csv")
    args = ap.parse_args()

    panel = load_team_game_panel(_parse_seasons(args.seasons))
    out_df = add_ewma_form(panel, span=args.span)
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "season",
        "week",
        "team",
        "opponent",
        "is_home",
        "won",
        "ewma_win",
        "ewma_diff",
        "ewma_win_diff",
        "ewma_diff_diff",
    ]
    out_df[cols].to_csv(path, index=False)
    print(f"rows={len(out_df)} span={args.span} wrote {path}")
    print(out_df[cols].head(8).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
