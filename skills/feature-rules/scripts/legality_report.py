#!/usr/bin/env python3
"""Screen a one-row-per-feature catalog for obvious legality problems."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_BANNED = "won,win,loss,result,score,points_for,points_against,point_diff,target,label"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV, Parquet, or JSON records file")
    parser.add_argument("--feature-col", default="feature", help="Column containing feature names")
    parser.add_argument(
        "--features",
        default="",
        help="Optional comma-separated feature names to select; default is every catalog row",
    )
    parser.add_argument(
        "--banned", default=DEFAULT_BANNED, help="Comma-separated exact forbidden names"
    )
    parser.add_argument(
        "--available-at-col",
        default="availability",
        help="Timing classification column: known_by_t, delayed, conditional, unknown, or post_t",
    )
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
    import pandas as pd

    args = parse_args()
    selected = [c.strip() for c in args.features.split(",") if c.strip()]
    banned = {c.strip().lower() for c in args.banned.split(",") if c.strip()}
    df = load_frame(args.input)
    if df.empty:
        raise SystemExit("input contains no rows to evaluate")
    required = [args.feature_col, args.available_at_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")

    names = df[args.feature_col]
    missing_names = int(names.isna().sum()) + int(
        names.dropna().astype(str).str.strip().eq("").sum()
    )
    if missing_names:
        raise SystemExit(f"{args.feature_col!r} contains {missing_names} blank feature names")
    df = df.copy()
    df[args.feature_col] = names.astype(str).str.strip()
    if selected:
        unknown_selected = sorted(set(selected).difference(df[args.feature_col]))
        if unknown_selected:
            raise SystemExit(
                f"selected features not found in catalog: {', '.join(unknown_selected)}"
            )
        df = df[df[args.feature_col].isin(selected)].copy()
    features = df[args.feature_col].tolist()
    duplicate_names = sorted(
        df.loc[df[args.feature_col].duplicated(False), args.feature_col].unique()
    )
    overlap = sorted(c for c in features if c.lower() in banned)

    aliases = {
        "known_by_t": "known_by_t",
        "known-by-t": "known_by_t",
        "pregame": "known_by_t",
        "pre-game": "known_by_t",
        "pre_decision": "known_by_t",
        "pre-decision": "known_by_t",
        "before": "known_by_t",
        "delayed": "delayed",
        "conditional": "conditional",
        "unknown": "unknown",
        "post_t": "post_t",
        "post-t": "post_t",
        "post_decision": "post_t",
        "post-decision": "post_t",
        "after": "post_t",
    }
    raw_availability = df[args.available_at_col]
    normalized = raw_availability.map(
        lambda value: aliases.get(str(value).strip().lower()) if not pd.isna(value) else None
    )
    unrecognized = sorted(
        raw_availability[normalized.isna() & raw_availability.notna()].astype(str).unique().tolist()
    )
    post_t = sorted(df.loc[normalized.eq("post_t"), args.feature_col].tolist())
    unresolved = sorted(
        df.loc[
            normalized.isna() | normalized.isin(["delayed", "conditional", "unknown"]),
            args.feature_col,
        ].tolist()
    )
    findings = [
        {
            "id": "forbidden_names",
            "status": "FAIL" if overlap else "PASS",
            "detail": overlap or "none",
        },
        {
            "id": "unique_feature_names",
            "status": "REVIEW" if duplicate_names else "PASS",
            "detail": duplicate_names or "all feature names are unique",
        },
        {
            "id": "availability_timing",
            "status": "FAIL" if post_t else "REVIEW" if unresolved or unrecognized else "PASS",
            "detail": {
                "post_t_features": post_t,
                "unresolved_features": unresolved,
                "unrecognized_values": unrecognized,
            },
        },
        {
            "id": "manual_evidence_review",
            "status": "REVIEW",
            "detail": (
                "Verify source timestamps, transforms, joins, shifts, and "
                "fold-fitting before LEGAL."
            ),
        },
    ]
    statuses = {finding["status"] for finding in findings}
    verdict = "ILLEGAL" if "FAIL" in statuses else "REVIEW REQUIRED"
    report = {
        "n_rows": int(len(df)),
        "features": features,
        "availability_counts": {
            str(key): int(value)
            for key, value in normalized.fillna("missing_or_unrecognized").value_counts().items()
        },
        "findings": findings,
        "verdict": verdict,
        "note": (
            "This screening helper cannot issue LEGAL; complete the "
            "feature-card evidence review."
        ),
    }
    text = json.dumps(report, indent=2)
    print(text)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {out}")
    return 2 if report["verdict"] == "ILLEGAL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
