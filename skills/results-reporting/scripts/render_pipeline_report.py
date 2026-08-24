#!/usr/bin/env python3
"""Render a markdown results report from sports-ds pipeline JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def render(doc: dict) -> str:
    sport = str(doc.get("sport") or "nfl").upper()
    seasons = doc.get("seasons_requested") or doc.get("seasons") or doc.get("config", {}).get("seasons")
    mean = doc.get("mean_metrics") or doc.get("means") or {}
    folds = doc.get("folds") or doc.get("by_season") or doc.get("season_metrics") or []
    rows_modeled = doc.get("rows_modeled") or doc.get("n_rows") or doc.get("n")
    target = doc.get("target") or ("won" if "log_loss" in json.dumps(mean) else "unknown")
    features = doc.get("feature_cols") or []
    elo_params = doc.get("elo_params")
    calibration = doc.get("calibration") or {}

    title = f"# Results: {sport} model"
    if elo_params:
        title = f"# Results: {sport} Elo baseline"
    elif target == "point_diff":
        title = f"# Results: {sport} margin model"
    elif "logistic_log_loss" in mean or "elo_logistic_log_loss" in mean:
        title = f"# Results: {sport} win model"

    lines = [
        title,
        "",
        "## Question",
        f"Evaluate a pre-game {sport} model on a team-game panel using only information available before the event.",
        "",
        "## Data",
        f"- Sport: {sport}",
        f"- Grain: team-game",
        f"- Seasons: {seasons}",
        f"- Rows modeled: {rows_modeled}",
        f"- Raw panel rows: {doc.get('rows_raw_panel', 'n/a')}",
        "",
        "## Methods",
        f"- Target: {target}",
        f"- Features: {features if features else 'see pipeline'}",
    ]
    if elo_params:
        lines.append(f"- Elo params: {elo_params}")
    lines.extend(
        [
            "- Models/baselines: see mean metrics keys",
            "- Decision time T: scheduled start / pre-game",
            "",
            "## Validation",
            "- Design: season walk-forward (train on past seasons only)",
            "- Primary metric: log-loss for win probs; MAE/RMSE for margins",
            "",
            "## Results",
            "",
            "### Mean walk-forward metrics",
            "```json",
            json.dumps(mean, indent=2),
            "```",
            "",
        ]
    )
    if calibration:
        lines.extend(
            [
                "### Calibration",
                "```json",
                json.dumps(calibration, indent=2),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "### Per-season folds",
            "```json",
            json.dumps(folds, indent=2),
            "```",
            "",
            "## Interpretation",
            "Compare candidate metrics to the constant/baseline entries. "
            "Improvement should appear on the held-out seasons, not only in-sample fit.",
            "",
            "## Limits",
            "- Form/Elo features are not a full player-availability model",
            "- Team-game panel doubles each game (home and away rows)",
            "- Public schedule data only unless otherwise stated",
            "",
            "## Reproduce",
            "```bash",
            "pip install -e .",
            "# multi-sport if needed:",
            'pip install -e ".[multi]"',
            f"# re-run the same sports-ds command that produced this JSON",
            "python skills/results-reporting/scripts/render_pipeline_report.py --json <this.json>",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", required=True)
    ap.add_argument("--out", default="data/pipeline_report.md")
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
