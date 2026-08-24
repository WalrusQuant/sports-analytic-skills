#!/usr/bin/env python3
"""Audit sports_ds pre-game features for common leakage failures."""

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


def audit_frame(df) -> dict:
    findings = []

    overlap = sorted(BANNED.intersection(set(FEATURE_COLS)))
    findings.append(
        {
            "id": "banned_in_feature_list",
            "status": "FAIL" if overlap else "PASS",
            "detail": overlap or "no banned outcome cols in FEATURE_COLS",
        }
    )

    first = df.sort_values(["team", "season", "week"]).groupby("team", as_index=False).head(1)
    na_rate = float(first["pre_win_pct"].isna().mean()) if "pre_win_pct" in df.columns else 0.0
    findings.append(
        {
            "id": "first_team_game_pre_features_na",
            "status": "PASS" if na_rate >= 0.9 else "FAIL",
            "detail": f"na_rate={na_rate:.3f}",
        }
    )

    hist = df[df.get("pre_games_played", 0) >= 1] if "pre_games_played" in df.columns else df
    same = float((hist["pre_win_pct"] == hist["won"]).mean()) if len(hist) else 1.0
    findings.append(
        {
            "id": "pre_win_pct_not_equal_current_won",
            "status": "FAIL" if same > 0.2 else "PASS",
            "detail": f"equal_rate={same:.3f}",
        }
    )

    missing_feats = [c for c in FEATURE_COLS if c not in df.columns]
    findings.append(
        {
            "id": "feature_cols_present",
            "status": "FAIL" if missing_feats else "PASS",
            "detail": missing_feats or "all FEATURE_COLS present",
        }
    )

    failed = [f for f in findings if f["status"] == "FAIL"]
    return {
        "n_rows": int(len(df)),
        "feature_cols": list(FEATURE_COLS),
        "findings": findings,
        "verdict": "NOT CLEAN" if failed else "CLEAN",
        "n_fail": len(failed),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seasons", default="2023-2024")
    p.add_argument("--out", default="")
    args = p.parse_args()

    df = add_pregame_form_features(load_team_game_panel(_parse_seasons(args.seasons)))
    report = audit_frame(df)
    text = json.dumps(report, indent=2)
    print(text)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    return 0 if report["verdict"] == "CLEAN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
