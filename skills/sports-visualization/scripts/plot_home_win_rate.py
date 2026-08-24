#!/usr/bin/env python3
"""Save a home win-rate by season bar chart for NFL."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from sports_ds.data.nfl import load_team_game_panel


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seasons", default="2018-2024")
    p.add_argument("--out", default="data/home_win_rate_by_season.png")
    args = p.parse_args()

    panel = load_team_game_panel(_parse_seasons(args.seasons))
    home = panel[panel["is_home"] == 1]
    rates = home.groupby("season")["won"].mean().sort_index()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(rates.index.astype(str), rates.values, color="steelblue", edgecolor="black")
    ax.axhline(0.5, color="red", linestyle="--", linewidth=1)
    ax.set_ylim(0.4, 0.7)
    ax.set_title(f"NFL home win rate by season (home rows only; n_games={home.game_id.nunique()})")
    ax.set_xlabel("season")
    ax.set_ylabel("home win rate")
    ax.grid(alpha=0.25, axis="y")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(rates.to_string())
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
