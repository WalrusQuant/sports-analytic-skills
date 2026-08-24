#!/usr/bin/env python3
"""Save a home win-rate by season bar chart for a sports_ds team-game panel."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def _load_panel(sport: str, seasons: list[int]):
    if sport == "nfl":
        from sports_ds.data.nfl import load_team_game_panel

        return load_team_game_panel(seasons)
    if sport == "nba":
        from sports_ds.data.nba import load_nba_team_game_panel

        return load_nba_team_game_panel(seasons)
    if sport == "mlb":
        from sports_ds.data.mlb import load_mlb_team_game_panel

        return load_mlb_team_game_panel(seasons)
    raise ValueError(f"unsupported sport: {sport}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sport", default="nfl", choices=["nfl", "nba", "mlb"])
    p.add_argument("--seasons", default="2018-2024")
    p.add_argument("--out", default="")
    args = p.parse_args()

    seasons = _parse_seasons(args.seasons)
    panel = _load_panel(args.sport, seasons)
    home = panel[panel["is_home"] == 1]
    rates = home.groupby("season")["won"].mean().sort_index()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(rates.index.astype(str), rates.values, color="steelblue", edgecolor="black")
    ax.axhline(0.5, color="red", linestyle="--", linewidth=1)
    ax.set_ylim(0.35, 0.75)
    n_games = int(home["game_id"].nunique())
    ax.set_title(
        f"{args.sport.upper()} home win rate by season "
        f"(home rows only; n_games={n_games}; seasons={args.seasons})"
    )
    ax.set_xlabel("season")
    ax.set_ylabel("home win rate")
    ax.grid(alpha=0.25, axis="y")
    out = Path(args.out or f"data/{args.sport}_home_win_rate_by_season.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(rates.to_string())
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
