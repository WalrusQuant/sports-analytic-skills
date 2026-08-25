#!/usr/bin/env python3
"""Audit user-provided pre-decision features for common leakage signals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


DEFAULT_BANNED = "won,win,loss,result,score,points_for,points_against,point_diff,target,label"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV, Parquet, or JSON records file")
    parser.add_argument("--target", required=True, help="Outcome column")
    parser.add_argument("--features", required=True, help="Comma-separated feature columns")
    parser.add_argument("--entity-col", help="Optional team/player/entity column")
    parser.add_argument("--time-col", help="Optional sortable event-time column")
    parser.add_argument("--banned", default=DEFAULT_BANNED, help="Comma-separated forbidden exact names")
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


def finding(identifier: str, status: str, detail) -> dict:
    if status not in {"PASS", "FAIL", "REVIEW"}:
        raise ValueError(f"invalid finding status: {status}")
    return {"id": identifier, "status": status, "detail": detail}


def main() -> int:
    args = parse_args()
    features = [c.strip() for c in args.features.split(",") if c.strip()]
    if not features:
        raise SystemExit("--features must name at least one column")
    required = [args.target, *features]
    if bool(args.entity_col) != bool(args.time_col):
        raise SystemExit("--entity-col and --time-col must be provided together")
    if args.entity_col:
        required.extend([args.entity_col, args.time_col])
    df = load_frame(args.input)
    if df.empty:
        raise SystemExit("input contains no rows to audit")
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    banned = {c.strip().lower() for c in args.banned.split(",") if c.strip()}
    overlap = sorted(c for c in features if c.lower() in banned or c == args.target)
    findings = [finding("forbidden_or_target_feature", "FAIL" if overlap else "PASS", overlap or "none")]

    exact_matches = []
    for col in features:
        comparable = df[[col, args.target]].dropna()
        if len(comparable) and bool((comparable[col] == comparable[args.target]).all()):
            exact_matches.append(col)
    findings.append(
        finding("feature_identical_to_target", "FAIL" if exact_matches else "PASS", exact_matches or "none")
    )

    duplicate_rate = float(df.duplicated().mean())
    findings.append(
        finding(
            "duplicate_rows",
            "REVIEW" if duplicate_rate > 0.01 else "PASS",
            f"duplicate_rate={duplicate_rate:.6f}",
        )
    )

    suspicious_corr = {}
    numeric = df[[args.target, *features]].select_dtypes(include="number")
    if args.target in numeric.columns:
        for col in numeric.columns:
            if col == args.target:
                continue
            corr = numeric[[col, args.target]].corr().iloc[0, 1]
            if corr == corr and abs(float(corr)) >= 0.995:
                suspicious_corr[col] = float(corr)
    findings.append(
        finding(
            "near_perfect_target_correlation",
            "REVIEW" if suspicious_corr else "PASS",
            suspicious_corr or "none",
        )
    )

    if args.entity_col:
        ordered = df.sort_values([args.entity_col, args.time_col])
        first = ordered.groupby(args.entity_col, as_index=False).head(1)
        first_null_rates = {c: float(first[c].isna().mean()) for c in features}
        findings.append(finding("first_event_history_review", "REVIEW", first_null_rates))

    findings.append(
        finding(
            "manual_pipeline_review",
            "REVIEW",
            (
                "Required: verify point-in-time source availability, transform ordering, "
                "join direction/cardinality, and fold-local preprocessing from lineage and code."
            ),
        )
    )

    failed = [item for item in findings if item["status"] == "FAIL"]
    # Matrix heuristics can find evidence of contamination, but cannot prove the
    # end-to-end pipeline clean. CLEAN is reserved for the completed manual audit.
    verdict = "NOT CLEAN" if failed else "REVIEW REQUIRED"
    report = {
        "n_rows": int(len(df)),
        "features": features,
        "findings": findings,
        "verdict": verdict,
        "limitations": (
            "Automated heuristics cannot prove point-in-time availability; verify joins, "
            "source timestamps, and feature shifts manually."
        ),
    }
    text = json.dumps(report, indent=2)
    print(text)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {out}")
    # Exit codes are intentional signals, not crashes:
    #   0 reserved (unused) — heuristics never auto-CLEAN
    #   1 REVIEW REQUIRED — continue; complete manual audit before trusting metrics
    #   2 NOT CLEAN — stop predictive claims until repaired and retested
    if failed:
        print(
            "exit=2 NOT CLEAN: stop predictive claims until repaired and retested",
            file=sys.stderr,
        )
        return 2
    print(
        "exit=1 REVIEW REQUIRED: not a hard failure; complete the manual audit "
        "before treating the matrix as CLEAN",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
