#!/usr/bin/env python3
"""Save a home-team point differential histogram for a sports_ds panel."""

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
    p.add_argument("--seasons", default="2023-2024")
    p.add_argument("--out", default="")
    args = p.parse_args()

    panel = _load_panel(args.sport, _parse_seasons(args.seasons))
    home = panel[panel["is_home"] == 1]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(home["point_diff"], bins=40, color="steelblue", edgecolor="black", alpha=0.85)
    ax.axvline(0.0, color="red", linestyle="--", linewidth=1.5)
    ax.set_title(
        f"{args.sport.upper()} home team point differential "
        f"(n={len(home)}, seasons={args.seasons})"
    )
    ax.set_xlabel("point_diff (home perspective)")
    ax.set_ylabel("games")
    ax.grid(alpha=0.25, axis="y")
    out = Path(args.out or f"data/{args.sport}_home_margin_hist.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(f"wrote {out} n={len(home)} mean_margin={home['point_diff'].mean():.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
