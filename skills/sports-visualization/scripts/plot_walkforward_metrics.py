#!/usr/bin/env python3
"""Bar chart of walk-forward metrics from sports-ds pipeline JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", required=True, help="pipeline JSON from sports-ds --json-out")
    p.add_argument("--metric", default="logistic_log_loss")
    p.add_argument("--baseline", default="constant_log_loss")
    p.add_argument("--out", default="data/walkforward_metrics.png")
    args = p.parse_args()

    doc = json.loads(Path(args.json).read_text(encoding="utf-8"))
    folds = doc.get("folds") or []
    if not folds:
        # support alternate key names
        folds = doc.get("by_season") or []
    if not folds:
        raise SystemExit("no folds found in JSON")

    seasons = [str(r.get("test_season", r.get("season"))) for r in folds]
    metric_vals = [float(r[args.metric]) for r in folds if args.metric in r]
    base_vals = [float(r[args.baseline]) for r in folds if args.baseline in r]
    if len(metric_vals) != len(seasons):
        raise SystemExit(f"metric {args.metric} missing on some folds")

    x = range(len(seasons))
    width = 0.38
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar([i - width / 2 for i in x], metric_vals, width=width, label=args.metric, color="steelblue")
    if len(base_vals) == len(seasons):
        ax.bar([i + width / 2 for i in x], base_vals, width=width, label=args.baseline, color="salmon")
    ax.set_xticks(list(x), seasons)
    sport = str(doc.get("sport", "sport")).upper()
    ax.set_title(
        f"{sport} walk-forward {args.metric} vs {args.baseline} "
        f"(n_folds={len(seasons)}; seasons={doc.get('seasons_requested')})"
    )
    ax.set_xlabel("test season")
    ax.set_ylabel(args.metric)
    ax.legend()
    ax.grid(alpha=0.25, axis="y")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
