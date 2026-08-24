#!/usr/bin/env python3
"""Render a markdown results report from sports-ds pipeline JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def render(doc: dict) -> str:
    seasons = doc.get("seasons") or doc.get("config", {}).get("seasons")
    mean = doc.get("mean_metrics") or doc.get("means") or {}
    by_season = doc.get("by_season") or doc.get("season_metrics") or []

    lines = [
        "# Results: NFL pre-game win model",
        "",
        "## Question",
        "Estimate pre-game P(team wins) on an NFL team-game panel using only information available before kickoff.",
        "",
        "## Data",
        f"- Source: nflverse schedules via `sports_ds.data.nfl` / nflreadpy",
        f"- Grain: team-game",
        f"- Seasons: {seasons}",
        f"- Rows evaluated: {doc.get('n_rows', doc.get('n', 'see pipeline'))}",
        "",
        "## Methods",
        "- Features: shifted pre-game form differentials (`sports_ds.features.team_form`)",
        "- Models: constant baseline, logistic baseline, hist gradient boosting (as configured)",
        "- Decision time T: scheduled kickoff",
        "",
        "## Validation",
        "- Design: season walk-forward (train on past seasons only)",
        "- Primary metric: log-loss",
        "",
        "## Results",
        "",
        "### Mean walk-forward metrics",
        "```json",
        json.dumps(mean, indent=2),
        "```",
        "",
        "### Per season",
        "```json",
        json.dumps(by_season, indent=2),
        "```",
        "",
        "## Interpretation",
        "Compare candidate log-loss to the constant baseline. Improvement should appear on multiple seasons, not one outlier year.",
        "",
        "## Limits",
        "- No injury/roster continuity model",
        "- Form features are not full opponent-adjusted EPA ratings",
        "- Team-game panel doubles each game (home and away rows)",
        "",
        "## Reproduce",
        "```bash",
        "pip install -e .",
        "sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win_pipeline.json",
        "python skills/results-reporting/scripts/render_pipeline_report.py --json data/nfl_win_pipeline.json",
        "```",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", required=True)
    ap.add_argument("--out", default="data/nfl_win_report.md")
    args = ap.parse_args()

    doc = json.loads(Path(args.json).read_text(encoding="utf-8"))
    md = render(doc)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(md)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
