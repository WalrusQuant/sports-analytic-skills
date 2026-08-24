#!/usr/bin/env python3
"""Smoke test for pybaseball import and a tiny season-table pull."""

from __future__ import annotations


def main() -> int:
    try:
        from pybaseball import batting_stats
    except ImportError as exc:
        print(f"FAIL: pybaseball not installed ({exc})")
        print("Install: pip install pybaseball")
        return 1

    print("pybaseball import ok")
    try:
        df = batting_stats(2024)
    except Exception as exc:
        print(f"FAIL: batting_stats(2024) errored: {exc}")
        return 2

    n = len(df)
    cols = list(df.columns)[:8]
    print(f"OK: batting_stats(2024) rows={n} sample_cols={cols}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
