#!/usr/bin/env python3
"""Print ordered group walk-forward fold sizes from a user-owned table."""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV, Parquet, or JSON records file")
    parser.add_argument("--split-col", required=True, help="Ordered season/date/group column")
    parser.add_argument(
        "--min-train-groups",
        type=int,
        default=2,
        help=(
            "Minimum ordered groups used only for training before the first test "
            "fold (default: 2). Example: seasons 2022-2024 with default 2 yields "
            "one test fold (2024). Use 1 to test 2023 and 2024."
        ),
    )
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
        labels = unique.astype(str).str.strip()
        season_matches = labels.str.extract(
            r"^(?P<start>\d{4})\s*[-/\N{EN DASH}\N{EM DASH}]\s*(?P<end>\d{2}|\d{4})$"
        )
        if season_matches.notna().to_numpy().all():
            starts = season_matches["start"].astype(int)
            raw_ends = season_matches["end"].astype(int)
            ends = raw_ends.where(raw_ends.ge(1000), (starts // 100) * 100 + raw_ends)
            ends = ends.where(ends.gt(starts), ends + 100)
            if not ends.eq(starts + 1).all():
                raise SystemExit(
                    f"{split_col!r} season ranges must span consecutive years"
                )
            order = starts
        elif labels.str.match(r"^\d{4}-\d{2}-\d{2}(?:[T ].*)?$").all():
            # Parse one value at a time so mixed ISO date/timestamp precision works
            # consistently across supported pandas versions.
            order = labels.map(lambda value: pd.to_datetime(value, errors="coerce", utc=True))
        else:
            raise SystemExit(
                f"{split_col!r} must contain numeric values, ISO dates/timestamps, "
                "or consecutive season ranges such as 2022-23 or 2022/2023; "
                "use an explicit numeric ordinal for other labels"
            )
        if order.isna().any():
            raise SystemExit(f"{split_col!r} contains an invalid date or season label")
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
        raise SystemExit(
            "not enough ordered groups to create a test fold: "
            f"have {len(groups)} group(s) {groups!r}, need more than "
            f"--min-train-groups={args.min_train_groups}"
        )
    n_test_folds = len(groups) - args.min_train_groups
    print(
        (
            f"# walk-forward: {len(groups)} ordered groups; "
            f"min_train_groups={args.min_train_groups}; "
            f"test_folds={n_test_folds} "
            f"({list(map(str, groups[args.min_train_groups:]))})"
        ),
        file=sys.stderr,
    )
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(["test_group", "n_train", "n_test", "train_groups"])
    for index in range(args.min_train_groups, len(groups)):
        test_group = groups[index]
        train_groups = groups[:index]
        n_train = int(df[args.split_col].isin(train_groups).sum())
        n_test = int((df[args.split_col] == test_group).sum())
        writer.writerow([test_group, n_train, n_test, "|".join(map(str, train_groups))])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
