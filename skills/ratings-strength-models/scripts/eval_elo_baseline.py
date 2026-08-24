#!/usr/bin/env python3
"""Walk-forward evaluate Elo baseline via sports_ds package pipeline."""

from __future__ import annotations

import argparse

from sports_ds.pipelines.nfl_elo_baseline import format_elo_report, run_nfl_elo_baseline


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seasons", default="2018-2024")
    p.add_argument("--k", type=float, default=20.0)
    p.add_argument("--home-adv", type=float, default=65.0)
    p.add_argument("--min-train-seasons", type=int, default=2)
    args = p.parse_args()

    result = run_nfl_elo_baseline(
        seasons=_parse_seasons(args.seasons),
        min_train_seasons=args.min_train_seasons,
        k=args.k,
        home_adv=args.home_adv,
    )
    print(format_elo_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
