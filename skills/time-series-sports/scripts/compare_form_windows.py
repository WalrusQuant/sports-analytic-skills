#!/usr/bin/env python3
"""Compare two precomputed feature sets using walk-forward logistic log loss."""

from __future__ import annotations

import argparse
import importlib.util
import math
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV, Parquet, or JSON records file")
    parser.add_argument("--target", required=True, help="Binary 0/1 outcome column")
    parser.add_argument("--split-col", required=True, help="Ordered season/date/group column")
    parser.add_argument("--features-a", required=True, help="Comma-separated first feature set")
    parser.add_argument("--features-b", required=True, help="Comma-separated second feature set")
    parser.add_argument("--min-train-groups", type=int, default=2)
    return parser.parse_args()


def load_local_ewma_module():
    path = Path(__file__).with_name("ewma_form.py")
    spec = importlib.util.spec_from_file_location("ewma_form_helper", path)
    if spec is None or spec.loader is None:
        raise SystemExit("could not load table reader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def log_loss(y, p) -> float:
    import numpy as np
    p = np.clip(p, 1e-15, 1 - 1e-15)
    return float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())


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
    a = [c.strip() for c in args.features_a.split(",") if c.strip()]
    b = [c.strip() for c in args.features_b.split(",") if c.strip()]
    if not a or not b or args.min_train_groups < 1:
        raise SystemExit("provide both feature sets and at least one training group")
    df = load_local_ewma_module().load_frame(args.input)
    required = list(dict.fromkeys([args.target, args.split_col, *a, *b]))
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    df = df[required].copy()
    import pandas as pd

    numeric = df[[*a, *b]].apply(lambda column: pd.to_numeric(column, errors="coerce"))
    invalid = df[[*a, *b]].notna() & numeric.isna()
    if invalid.any().any():
        bad = [column for column in [*a, *b] if invalid[column].any()]
        raise SystemExit(f"feature columns contain non-numeric values: {', '.join(dict.fromkeys(bad))}")
    df[[*a, *b]] = numeric.astype(float)
    target = pd.to_numeric(df[args.target], errors="coerce")
    if (df[args.target].notna() & target.isna()).any():
        raise SystemExit(f"{args.target!r} must be numeric binary 0/1")
    df[args.target] = target
    df = df.dropna().copy()
    if df.empty:
        raise SystemExit("no complete rows remain for the matched feature-set comparison")
    if not set(df[args.target].unique()) <= {0, 1}:
        raise SystemExit(f"{args.target!r} must contain only 0/1 values")
    try:
        import numpy as np
        from sklearn.linear_model import LogisticRegression
    except ImportError as exc:
        raise SystemExit(
            "numpy and scikit-learn are required; install them with: "
            "python -m pip install numpy scikit-learn"
        ) from exc
    if not np.isfinite(df[[*a, *b]].to_numpy(dtype=float)).all():
        raise SystemExit("feature columns must contain only finite values")
    groups = ordered_groups(df[args.split_col], args.split_col)
    if len(groups) <= args.min_train_groups:
        raise SystemExit("not enough ordered groups to create a test fold")
    print("test_group,n_test,constant_ll,features_a_ll,features_b_ll")
    for index in range(args.min_train_groups, len(groups)):
        test_group = groups[index]
        train = df[df[args.split_col].isin(groups[:index])]
        test = df[df[args.split_col] == test_group]
        y_train = train[args.target].astype(int).to_numpy()
        y_test = test[args.target].astype(int).to_numpy()
        if len(np.unique(y_train)) < 2:
            raise SystemExit(f"training fold before {test_group!r} has only one target class")
        pa = LogisticRegression(max_iter=2000).fit(train[a], y_train).predict_proba(test[a])[:, 1]
        pb = LogisticRegression(max_iter=2000).fit(train[b], y_train).predict_proba(test[b])[:, 1]
        constant = np.full(len(test), y_train.mean())
        print(f"{test_group},{len(test)},{log_loss(y_test, constant):.6f},{log_loss(y_test, pa):.6f},{log_loss(y_test, pb):.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
