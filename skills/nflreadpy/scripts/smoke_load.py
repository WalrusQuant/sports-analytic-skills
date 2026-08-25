#!/usr/bin/env python3
"""Smoke test for nflreadpy import and a tiny schedules load."""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--season", type=int, default=0, help="Season to probe; 0 uses current")
    args = parser.parse_args()
    if args.season and not 1999 <= args.season <= 2100:
        parser.error("--season must be between 1999 and 2100")
    try:
        import nflreadpy as nfl
    except ImportError as exc:
        print(f"FAIL: nflreadpy not installed ({exc})")
        print("Install: pip install nflreadpy")
        return 1

    season = args.season or nfl.get_current_season()
    print(f"nflreadpy import ok; current_season={season}")

    try:
        schedules = nfl.load_schedules([season])
    except Exception as exc:  # network/cache failures should be visible
        print(f"FAIL: load_schedules({season}) errored: {exc}")
        return 2

    n = schedules.height if hasattr(schedules, "height") else len(schedules)
    if n == 0:
        print(f"FAIL: load_schedules({season}) returned zero rows")
        return 3
    print(f"OK: load_schedules({season}) rows={n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
