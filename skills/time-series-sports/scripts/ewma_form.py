#!/usr/bin/env python3
"""Create shifted EWMA features from a user-owned event table."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV, Parquet, or JSON records file")
    parser.add_argument("--entity-col", required=True, help="Team, player, or entity column")
    parser.add_argument("--time-col", required=True, help="Sortable event time or sequence column")
    parser.add_argument(
        "--order-col",
        help="Optional strict event sequence used when time values can tie",
    )
    parser.add_argument("--values", required=True, help="Comma-separated numeric columns to summarize")
    parser.add_argument("--group-cols", default="", help="Extra reset columns, such as season")
    parser.add_argument("--span", type=float, default=5.0)
    parser.add_argument("--out", required=True, help="Output CSV or Parquet path")
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


def add_shifted_ewma(
    df,
    entity_col: str,
    time_col: str,
    order_col: str | None,
    values: list[str],
    group_cols: list[str],
    span: float,
):
    keys = [*group_cols, entity_col]
    order = order_col or time_col
    out = df.sort_values([*keys, order], kind="stable").copy()
    grouped = out.groupby(keys, sort=False, group_keys=False)
    for col in values:
        prior = grouped[col].shift(1)
        out[f"pre_ewma_{col}"] = prior.groupby([out[k] for k in keys], sort=False).transform(
            lambda series: series.ewm(span=span, adjust=False).mean()
        )
    return out


def main() -> int:
    args = parse_args()
    if args.span <= 1:
        raise SystemExit("--span must be greater than 1")
    values = [c.strip() for c in args.values.split(",") if c.strip()]
    group_cols = [c.strip() for c in args.group_cols.split(",") if c.strip()]
    if not values:
        raise SystemExit("--values must name at least one column")
    df = load_frame(args.input)
    required = [
        args.entity_col,
        args.time_col,
        *([args.order_col] if args.order_col else []),
        *group_cols,
        *values,
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    nonnumeric = [c for c in values if not str(df[c].dtype).startswith(("int", "float"))]
    if nonnumeric:
        raise SystemExit(f"value columns must be numeric: {', '.join(nonnumeric)}")
    keys = [*group_cols, args.entity_col]
    sequence_col = args.order_col or args.time_col
    if df.duplicated([*keys, sequence_col]).any():
        hint = (
            "provide a strictly ordered --order-col"
            if not args.order_col
            else f"{args.order_col!r} must be unique within each entity/reset group"
        )
        raise SystemExit(f"ambiguous event order: {hint}")
    out_df = add_shifted_ewma(
        df,
        args.entity_col,
        args.time_col,
        args.order_col,
        values,
        group_cols,
        args.span,
    )
    out = Path(args.out)
    if Path(args.input).resolve() == out.resolve():
        raise SystemExit("--out must differ from --input")
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix.lower() == ".csv":
        out_df.to_csv(out, index=False)
    elif out.suffix.lower() in {".parquet", ".pq"}:
        out_df.to_parquet(out, index=False)
    else:
        raise SystemExit("--out must end in .csv, .parquet, or .pq")
    created = [f"pre_ewma_{c}" for c in values]
    print(f"rows={len(out_df)} span={args.span} created={','.join(created)} wrote {out}")
    print(out_df[[*required, *created]].head(8).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
