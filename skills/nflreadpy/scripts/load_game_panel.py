#!/usr/bin/env python3
"""Load NFL schedules for given seasons and write a parquet panel."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_seasons(raw: str) -> list[int]:
    parts = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            a, b = chunk.split("-", 1)
            parts.extend(range(int(a), int(b) + 1))
        else:
            parts.append(int(chunk))
    return sorted(set(parts))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seasons", required=True, help="e.g. 2023,2024 or 2020-2024")
    parser.add_argument("--out", default="data/nfl_schedules.parquet")
    args = parser.parse_args()

    try:
        import nflreadpy as nfl
    except ImportError as exc:
        print(f"FAIL: nflreadpy not installed ({exc})")
        return 1

    seasons = parse_seasons(args.seasons)
    df = nfl.load_schedules(seasons)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    if hasattr(df, "write_parquet"):
        df.write_parquet(out)
        n = df.height
    else:
        df.to_parquet(out, index=False)
        n = len(df)

    print(f"OK: wrote {n} rows for seasons={seasons} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
