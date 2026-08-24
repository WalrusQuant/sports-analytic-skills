#!/usr/bin/env python3
"""Measure probability calibration from observed outcomes and predictions."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV, Parquet, or JSON records file")
    parser.add_argument("--target", required=True, help="Binary 0/1 outcome column")
    parser.add_argument("--probability", required=True, help="Predicted probability column")
    parser.add_argument("--bins", type=int, default=10)
    parser.add_argument("--group-col", help="Optional fold or season column for group metrics")
    parser.add_argument("--filter-col", help="Optional column used to select one evaluation perspective")
    parser.add_argument("--filter-value", help="String value required in --filter-col")
    parser.add_argument("--out", help="Optional JSON output path")
    return parser.parse_args()


def load_frame(path: str):
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit("pandas is required; install it with: python -m pip install pandas") from exc
    suffix = Path(path).suffix.lower()
    if suffix == ".csv": return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}: return pd.read_parquet(path)
    if suffix in {".json", ".jsonl", ".ndjson"}: return pd.read_json(path, lines=suffix != ".json")
    raise SystemExit("--input must be CSV, Parquet, JSON, JSONL, or NDJSON")


def metrics(rows, target: str, probability: str, bins: int) -> dict:
    y = [float(v) for v in rows[target]]
    p = [float(v) for v in rows[probability]]
    n = len(y)
    brier = sum((yi - pi) ** 2 for yi, pi in zip(y, p)) / n
    eps = 1e-15
    log_loss = -sum(
        yi * math.log(min(max(pi, eps), 1 - eps))
        + (1 - yi) * math.log(1 - min(max(pi, eps), 1 - eps))
        for yi, pi in zip(y, p)
    ) / n
    table = []
    ece = 0.0
    for index in range(bins):
        lower, upper = index / bins, (index + 1) / bins
        positions = [i for i, value in enumerate(p) if lower <= value <= upper and (index == bins - 1 or value < upper)]
        if not positions:
            continue
        mean_p = sum(p[i] for i in positions) / len(positions)
        rate = sum(y[i] for i in positions) / len(positions)
        ece += len(positions) / n * abs(rate - mean_p)
        table.append({"bin": index + 1, "lower": lower, "upper": upper, "n": len(positions), "mean_probability": mean_p, "observed_rate": rate})
    return {"n": n, "brier": brier, "log_loss": log_loss, "ece": ece, "calibration_table": table}


def main() -> int:
    args = parse_args()
    if args.bins < 2:
        raise SystemExit("--bins must be at least 2")
    if bool(args.filter_col) != bool(args.filter_value):
        raise SystemExit("--filter-col and --filter-value must be provided together")
    df = load_frame(args.input)
    required = [args.target, args.probability]
    required += [args.group_col] if args.group_col else []
    required += [args.filter_col] if args.filter_col else []
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    clean = df[required].dropna().copy()
    if args.filter_col:
        clean = clean[clean[args.filter_col].astype(str) == args.filter_value].copy()
    if clean.empty:
        raise SystemExit("no complete rows to evaluate")
    if not set(clean[args.target].unique()) <= {0, 1, False, True}:
        raise SystemExit(f"{args.target!r} must contain only 0/1 values")
    if not clean[args.probability].between(0, 1).all():
        raise SystemExit(f"{args.probability!r} must be between 0 and 1")
    report = metrics(clean, args.target, args.probability, args.bins)
    if args.filter_col:
        report["filter"] = {"column": args.filter_col, "value": args.filter_value}
    if args.group_col:
        report["groups"] = {
            str(group): metrics(part, args.target, args.probability, args.bins)
            for group, part in clean.groupby(args.group_col, sort=True)
        }
    report["verdict"] = "inspect-sample-size" if report["n"] < 100 else ("well-calibrated" if report["ece"] <= 0.05 else "recalibration-candidate")
    text = json.dumps(report, indent=2)
    print(text)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
