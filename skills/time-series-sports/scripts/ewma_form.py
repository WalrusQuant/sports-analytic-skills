#!/usr/bin/env python3
"""Create shifted EWMA features from a user-owned event table."""

from __future__ import annotations

import argparse
from pathlib import Path


def normalized_order_values(series, column: str):
    """Return finite numeric or UTC timestamp sort keys for a required column."""
    import numpy as np
    import pandas as pd

    if series.isna().any():
        raise SystemExit(f"{column!r} must not contain null values")
    if pd.api.types.is_bool_dtype(series.dtype):
        raise SystemExit(f"{column!r} must not use boolean values")
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().all():
        values = numeric.to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise SystemExit(f"{column!r} must contain finite ordering values")
        return pd.Series(values, index=series.index)
    timestamps = pd.to_datetime(series, errors="coerce", utc=True, format="mixed")
    if timestamps.isna().any():
        raise SystemExit(f"{column!r} must contain numeric or parseable timestamp values")
    return pd.Series(timestamps.astype("int64"), index=series.index)


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
    out = df.copy()
    sort_key = "__ewma_sort_key"
    while sort_key in out.columns:
        sort_key += "_"
    out[sort_key] = normalized_order_values(out[order], order)
    out = out.sort_values([*keys, sort_key], kind="stable").copy()
    grouped = out.groupby(keys, sort=False, group_keys=False)
    for col in values:
        prior = grouped[col].shift(1)
        out[f"pre_ewma_{col}"] = prior.groupby([out[k] for k in keys], sort=False).transform(
            lambda series: series.ewm(span=span, adjust=False).mean()
        )
    return out.drop(columns=[sort_key])


def main() -> int:
    args = parse_args()
    if args.span <= 1:
        raise SystemExit("--span must be greater than 1")
    values = [c.strip() for c in args.values.split(",") if c.strip()]
    group_cols = [c.strip() for c in args.group_cols.split(",") if c.strip()]
    if not values:
        raise SystemExit("--values must name at least one column")
    named_roles = [args.entity_col, args.time_col, *group_cols, *values]
    named_roles += [args.order_col] if args.order_col else []
    if len(set(named_roles)) != len(named_roles):
        raise SystemExit("entity, time, order, reset-group, and value columns must not overlap")
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
    import numpy as np
    import pandas as pd

    key_columns = [*group_cols, args.entity_col]
    if df[key_columns].isna().any().any():
        raise SystemExit("entity and reset-group columns must not contain null values")
    nonnumeric = [
        c
        for c in values
        if not pd.api.types.is_numeric_dtype(df[c].dtype)
    ]
    if nonnumeric:
        raise SystemExit(f"value columns must use numeric or boolean dtypes: {', '.join(nonnumeric)}")
    numeric_values = df[values].to_numpy(dtype=float, na_value=np.nan)
    if np.isinf(numeric_values).any():
        raise SystemExit("value columns must not contain infinite values")
    keys = [*group_cols, args.entity_col]
    sequence_col = args.order_col or args.time_col
    sequence_values = normalized_order_values(df[sequence_col], sequence_col)
    time_values = normalized_order_values(df[args.time_col], args.time_col)
    ordering = df[keys].copy()
    ordering["__sequence"] = sequence_values
    ordering["__time"] = time_values
    if ordering.duplicated([*keys, "__sequence"]).any():
        hint = (
            "provide a strictly ordered --order-col"
            if not args.order_col
            else f"{args.order_col!r} must be unique within each entity/reset group"
        )
        raise SystemExit(f"ambiguous event order: {hint}")
    ordered = ordering.sort_values([*keys, "__sequence"], kind="stable")
    time_reverses = ordered.groupby(keys, sort=False)["__time"].diff().lt(0)
    if time_reverses.any():
        raise SystemExit(
            f"{sequence_col!r} orders at least one event before an earlier {args.time_col!r} value"
        )
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
