#!/usr/bin/env python3
"""Print ordered group walk-forward fold sizes from a user-owned table."""

from __future__ import annotations

import argparse
import math
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV, Parquet, or JSON records file")
    parser.add_argument("--split-col", required=True, help="Ordered season/date/group column")
    parser.add_argument("--min-train-groups", type=int, default=2)
    parser.add_argument("--required-cols", default="", help="Comma-separated columns that must be non-null")
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


def ordered_groups(series, split_col: str) -> list:
    import pandas as pd

    unique = series.drop_duplicates()
    if pd.api.types.is_bool_dtype(unique.dtype):
        raise SystemExit(f"{split_col!r} must not use boolean split values")
    numeric = pd.to_numeric(unique, errors="coerce")
    if numeric.notna().all():
        if not numeric.map(lambda value: math.isfinite(float(value))).all():
            raise SystemExit(f"{split_col!r} contains non-finite split values")
        order = numeric
    else:
        order = pd.to_datetime(unique, errors="coerce", utc=True, format="mixed")
        if order.isna().any():
            raise SystemExit(
                f"{split_col!r} must contain numeric or parseable chronological values"
            )
    ranked = pd.DataFrame({"group": unique.to_list(), "order": order.to_list()})
    if ranked["order"].duplicated().any():
        raise SystemExit(f"{split_col!r} contains ambiguous values with the same ordering key")
    return ranked.sort_values("order", kind="stable")["group"].to_list()


def main() -> int:
    args = parse_args()
    if args.min_train_groups < 1:
        raise SystemExit("--min-train-groups must be at least 1")
    required = [c.strip() for c in args.required_cols.split(",") if c.strip()]
    df = load_frame(args.input)
    missing = [c for c in [args.split_col, *required] if c not in df.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    df = df.dropna(subset=[args.split_col, *required])
    groups = ordered_groups(df[args.split_col], args.split_col)
    if len(groups) <= args.min_train_groups:
        raise SystemExit("not enough ordered groups to create a test fold")
    print("test_group,n_train,n_test,train_groups")
    for index in range(args.min_train_groups, len(groups)):
        test_group = groups[index]
        train_groups = groups[:index]
        n_train = int(df[args.split_col].isin(train_groups).sum())
        n_test = int((df[args.split_col] == test_group).sum())
        print(f"{test_group},{n_train},{n_test},{'|'.join(map(str, train_groups))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
