#!/usr/bin/env python3
"""Check candidate feature names and timing metadata for pre-decision legality."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_BANNED = "won,win,loss,result,score,points_for,points_against,point_diff,target,label"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV, Parquet, or JSON records file")
    parser.add_argument("--features", required=True, help="Comma-separated candidate feature columns")
    parser.add_argument("--banned", default=DEFAULT_BANNED, help="Comma-separated exact forbidden names")
    parser.add_argument("--available-at-col", help="Optional metadata column; values must be pregame/pre-decision")
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


def main() -> int:
    args = parse_args()
    features = [c.strip() for c in args.features.split(",") if c.strip()]
    banned = {c.strip().lower() for c in args.banned.split(",") if c.strip()}
    if not features:
        raise SystemExit("--features must name at least one column")
    df = load_frame(args.input)
    if df.empty:
        raise SystemExit("input contains no rows to evaluate")
    required = features + ([args.available_at_col] if args.available_at_col else [])
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    overlap = sorted(c for c in features if c.lower() in banned)
    availability_finding = {
        "id": "availability_timing",
        "status": "UNKNOWN",
        "detail": "no availability metadata column supplied",
    }
    if args.available_at_col:
        allowed = {"pregame", "pre-game", "pre_decision", "pre-decision", "before"}
        availability = df[args.available_at_col]
        missing_count = int(availability.isna().sum())
        unknown_values = sorted(
            {
                str(value)
                for value in availability.dropna().unique()
                if str(value).strip().lower() not in allowed
            }
        )
        failed = bool(missing_count or unknown_values)
        availability_finding = {
            "id": "availability_timing",
            "status": "FAIL" if failed else "PASS",
            "detail": {
                "missing_count": missing_count,
                "unknown_values": unknown_values,
            }
            if failed
            else "all rows have recognized pre-decision availability",
        }
    findings = [
        {"id": "forbidden_names", "status": "FAIL" if overlap else "PASS", "detail": overlap or "none"},
        availability_finding,
    ]
    statuses = {finding["status"] for finding in findings}
    verdict = "ILLEGAL" if "FAIL" in statuses else ("REVIEW_REQUIRED" if "UNKNOWN" in statuses else "LEGAL_CANDIDATE")
    report = {
        "n_rows": int(len(df)),
        "features": features,
        "null_rates": {c: float(df[c].isna().mean()) for c in features},
        "findings": findings,
        "verdict": verdict,
        "note": "A passing name/timing check still requires source-level and shift verification.",
    }
    text = json.dumps(report, indent=2)
    print(text)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {out}")
    return 0 if report["verdict"] == "LEGAL_CANDIDATE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
