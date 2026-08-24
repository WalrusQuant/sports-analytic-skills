#!/usr/bin/env python3
"""Print calibration metrics for all rows and user-selected segments."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV, Parquet, or JSON records file")
    parser.add_argument("--target", required=True, help="Binary 0/1 outcome column")
    parser.add_argument("--probability", required=True, help="Predicted probability column")
    parser.add_argument("--segment-col", help="Optional categorical segment column")
    parser.add_argument("--filter-col", help="Optional column used to select one evaluation perspective")
    parser.add_argument("--filter-value", help="String value required in --filter-col")
    parser.add_argument("--bins", type=int, default=10)
    return parser.parse_args()


def load_report_module():
    path = Path(__file__).with_name("calibration_report.py")
    spec = importlib.util.spec_from_file_location("calibration_report_helper", path)
    if spec is None or spec.loader is None:
        raise SystemExit("could not load calibration metric helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    args = parse_args()
    if args.bins < 2:
        raise SystemExit("--bins must be at least 2")
    if bool(args.filter_col) != bool(args.filter_value):
        raise SystemExit("--filter-col and --filter-value must be provided together")
    helper = load_report_module()
    df = helper.load_frame(args.input)
    required = [args.target, args.probability]
    required += [args.segment_col] if args.segment_col else []
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
    segments = [("all", clean)]
    if args.segment_col:
        segments.extend((f"{args.segment_col}={value}", part) for value, part in clean.groupby(args.segment_col, sort=True))
    segments.extend([
        ("tail_low", clean[clean[args.probability] < 0.2]),
        ("tail_high", clean[clean[args.probability] > 0.8]),
    ])
    print("segment,n,brier,log_loss,ece")
    for name, part in segments:
        if part.empty:
            print(f"{name},0,,,")
            continue
        result = helper.metrics(part, args.target, args.probability, args.bins)
        print(f"{name},{result['n']},{result['brier']:.6f},{result['log_loss']:.6f},{result['ece']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
