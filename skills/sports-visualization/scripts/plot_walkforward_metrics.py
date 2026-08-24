#!/usr/bin/env python3
"""Bar chart of walk-forward metrics from a user-owned JSON report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", required=True, help="JSON object containing a folds array")
    p.add_argument("--fold-col", default="fold", help="fold-label field in each row")
    p.add_argument("--metric", required=True, help="candidate metric field")
    p.add_argument("--baseline", required=True, help="baseline metric field")
    p.add_argument("--title", help="optional chart title")
    p.add_argument("--out", required=True, help="destination image path")
    args = p.parse_args()

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit("This command requires matplotlib. Install it with: pip install matplotlib") from exc

    source = Path(args.json)
    if not source.is_file():
        raise SystemExit(f"--json does not exist: {source}")
    try:
        doc = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid JSON artifact: {exc}") from exc
    if not isinstance(doc, dict) or not isinstance(doc.get("folds"), list):
        raise SystemExit("JSON root must be an object containing a folds array")
    folds = doc["folds"]
    if not folds or not all(isinstance(row, dict) for row in folds):
        raise SystemExit("folds must contain at least one object")
    required = [args.fold_col, args.metric, args.baseline]
    for index, row in enumerate(folds):
        missing = [field for field in required if field not in row]
        if missing:
            raise SystemExit(
                f"fold {index} is missing required fields: {', '.join(missing)}"
            )
    seasons = [str(row[args.fold_col]) for row in folds]
    try:
        metric_vals = [float(row[args.metric]) for row in folds]
        base_vals = [float(row[args.baseline]) for row in folds]
    except (TypeError, ValueError) as exc:
        raise SystemExit("metric and baseline fields must be numeric") from exc
    import math
    if not all(math.isfinite(value) for value in [*metric_vals, *base_vals]):
        raise SystemExit("metric and baseline fields must be finite")

    x = range(len(seasons))
    width = 0.38
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.bar([i - width / 2 for i in x], metric_vals, width=width, label=args.metric, color="steelblue")
    ax.bar([i + width / 2 for i in x], base_vals, width=width, label=args.baseline, color="salmon")
    ax.set_xticks(list(x), seasons)
    title = args.title or (
        f"Walk-forward {args.metric} vs {args.baseline} "
        f"(n_folds={len(seasons)})"
    )
    ax.set_title(title, wrap=True, pad=14)
    ax.set_xlabel(args.fold_col)
    ax.set_ylabel(args.metric)
    ax.legend()
    ax.grid(alpha=0.25, axis="y")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
