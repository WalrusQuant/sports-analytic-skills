#!/usr/bin/env python3
"""Report legality checks for sports_ds pre-game feature columns."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.pipelines.nfl_win_model import FEATURE_COLS

BANNED = {"won", "points_for", "points_against", "point_diff"}


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seasons", default="2023-2024")
    p.add_argument("--out", default="data/feature_legality.json")
    args = p.parse_args()

    df = add_pregame_form_features(load_team_game_panel(_parse_seasons(args.seasons)))
    overlap = sorted(BANNED.intersection(FEATURE_COLS))
    first = df.sort_values(["team", "season", "week"]).groupby("team", as_index=False).head(1)
    report = {
        "feature_cols": list(FEATURE_COLS),
        "banned_overlap": overlap,
        "banned_overlap_status": "FAIL" if overlap else "PASS",
        "first_team_game_pre_win_pct_na_rate": float(first["pre_win_pct"].isna().mean()),
        "null_rates": {c: float(df[c].isna().mean()) for c in FEATURE_COLS if c in df.columns},
        "n_rows": int(len(df)),
    }
    report["verdict"] = "LEGAL_CANDIDATE" if report["banned_overlap_status"] == "PASS" else "ILLEGAL"
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"wrote {out}")
    return 0 if report["verdict"] == "LEGAL_CANDIDATE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
