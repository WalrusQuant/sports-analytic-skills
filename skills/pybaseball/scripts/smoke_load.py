#!/usr/bin/env python3
"""Smoke test for pybaseball import and a tiny season-table pull."""

from __future__ import annotations

import argparse
import importlib.metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--season", type=int, default=2024)
    args = parser.parse_args()
    if not 1871 <= args.season <= 2100:
        parser.error("--season must be between 1871 and 2100")
    try:
        from pybaseball import batting_stats
    except ImportError as exc:
        print(f"FAIL: pybaseball not installed ({exc})")
        print("Install: pip install pybaseball")
        return 1

    try:
        version = importlib.metadata.version("pybaseball")
    except importlib.metadata.PackageNotFoundError:
        version = "unknown"
    print(f"pybaseball import ok; version={version}; probe=FanGraphs batting_stats")
    try:
        df = batting_stats(args.season)
    except Exception as exc:
        print(f"FAIL: batting_stats({args.season}) errored: {exc}")
        return 2

    n = len(df)
    if n == 0:
        print(
            f"FAIL: batting_stats({args.season}) returned zero rows; "
            "an empty provider response is not success"
        )
        return 3
    if not hasattr(df, "columns") or len(df.columns) == 0:
        print(f"FAIL: batting_stats({args.season}) returned no columns")
        return 4
    cols = list(df.columns)[:8]
    print(f"OK: batting_stats({args.season}) rows={n} sample_cols={cols}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
