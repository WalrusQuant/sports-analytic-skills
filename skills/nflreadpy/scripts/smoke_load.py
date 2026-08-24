#!/usr/bin/env python3
"""Smoke test for nflreadpy import and a tiny schedules load."""

from __future__ import annotations


def main() -> int:
    try:
        import nflreadpy as nfl
    except ImportError as exc:
        print(f"FAIL: nflreadpy not installed ({exc})")
        print("Install: pip install nflreadpy")
        return 1

    season = nfl.get_current_season()
    print(f"nflreadpy import ok; current_season={season}")

    try:
        schedules = nfl.load_schedules([season])
    except Exception as exc:  # network/cache failures should be visible
        print(f"FAIL: load_schedules({season}) errored: {exc}")
        return 2

    n = schedules.height if hasattr(schedules, "height") else len(schedules)
    print(f"OK: load_schedules({season}) rows={n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
