"""Exploratory summaries for sports tables."""

from __future__ import annotations

from typing import Any

import pandas as pd


def summarize_frame(df: pd.DataFrame, name: str = "frame") -> dict[str, Any]:
    out: dict[str, Any] = {
        "name": name,
        "rows": int(len(df)),
        "cols": int(df.shape[1]),
        "columns": list(df.columns),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "null_counts": {c: int(v) for c, v in df.isna().sum().items() if int(v) > 0},
        "duplicate_rows": int(df.duplicated().sum()),
    }
    return out


def summarize_team_game_panel(df: pd.DataFrame) -> dict[str, Any]:
    base = summarize_frame(df, name="team_game_panel")
    base["seasons"] = sorted(df["season"].dropna().unique().tolist()) if "season" in df.columns else []
    base["n_teams"] = int(df["team"].nunique()) if "team" in df.columns else None
    base["n_games"] = int(df["game_id"].nunique()) if "game_id" in df.columns else None
    if "won" in df.columns:
        base["home_win_rate"] = float(df.loc[df["is_home"] == 1, "won"].mean()) if "is_home" in df.columns else None
        base["overall_win_rate"] = float(df["won"].mean())
    if "point_diff" in df.columns:
        base["point_diff_mean"] = float(df["point_diff"].mean())
        base["point_diff_std"] = float(df["point_diff"].std())
    if {"season", "week"}.issubset(df.columns):
        coverage = (
            df.groupby(["season", "week"], as_index=False)
            .size()
            .rename(columns={"size": "team_game_rows"})
        )
        base["season_week_coverage_head"] = coverage.head(10).to_dict(orient="records")
    return base


def format_summary(summary: dict[str, Any]) -> str:
    lines = [f"== {summary.get('name', 'summary')} =="]
    for k, v in summary.items():
        if k in {"name", "columns", "dtypes", "season_week_coverage_head"}:
            continue
        lines.append(f"{k}: {v}")
    if summary.get("null_counts"):
        lines.append(f"null_counts: {summary['null_counts']}")
    return "\n".join(lines)
