"""Translate toolkit pipeline results into portable skill artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def win_fold_metrics_payload(result: dict[str, Any]) -> dict[str, Any]:
    """Fold JSON matching the sports-ds-bridge / results-reporting contract."""
    folds = []
    for row in result.get("folds") or []:
        folds.append(
            {
                "fold": str(row.get("fold", row.get("test_season"))),
                "model": row.get("logistic_log_loss"),
                "baseline": row.get("constant_log_loss"),
                "n_test": row.get("n_test"),
            }
        )
    return {
        "task": result.get("task", "binary classification"),
        "validation": result.get("validation", "season walk-forward"),
        "primary_metric": result.get("primary_metric", "log_loss"),
        "sport": result.get("sport"),
        "folds": folds,
    }


def write_win_skill_artifacts(result: dict[str, Any], out_dir: str | Path) -> dict[str, Path]:
    """Write fold-metrics JSON and a prediction CSV a standalone skill can consume."""
    dest = Path(out_dir)
    dest.mkdir(parents=True, exist_ok=True)
    folds_path = dest / "fold_metrics.json"
    preds_path = dest / "predictions.csv"
    folds_path.write_text(
        json.dumps(win_fold_metrics_payload(result), indent=2, default=str),
        encoding="utf-8",
    )
    rows = list(result.get("predictions") or [])
    if rows:
        fieldnames = list(rows[0].keys())
        with preds_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    else:
        preds_path.write_text("season,fold,game_id,team,is_home,y_true,p_pred\n", encoding="utf-8")
    return {"folds": folds_path, "predictions": preds_path}
