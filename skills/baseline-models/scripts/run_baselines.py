#!/usr/bin/env python3
"""Compare constant and logistic baselines with ordered group walk-forward folds."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV, Parquet, or JSON records file")
    parser.add_argument("--target", required=True, help="Binary 0/1 outcome column")
    parser.add_argument("--features", required=True, help="Comma-separated numeric feature columns")
    parser.add_argument("--split-col", required=True, help="Ordered season/date/group column")
    parser.add_argument("--id-cols", default="", help="Comma-separated identifiers to preserve")
    parser.add_argument(
        "--min-train-groups",
        type=int,
        default=2,
        help=(
            "Minimum ordered groups used only for training before the first test "
            "fold (default: 2). With seasons [2022,2023,2024] and default 2, only "
            "2024 is tested (train on 2022+2023). Use 1 to also test 2023."
        ),
    )
    parser.add_argument("--out", help="Optional fold artifact (.json)")
    parser.add_argument(
        "--predictions-out",
        help="Optional held-out prediction records (.csv, .parquet, or .json)",
    )
    return parser.parse_args()


def load_frame(path: str):
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit("pandas is required; install it with: python -m pip install pandas") from exc
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if suffix in {".json", ".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=suffix != ".json")
    raise SystemExit("--input must be CSV, Parquet, JSON, JSONL, or NDJSON")


def write_predictions(frame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        frame.to_csv(path, index=False)
    elif suffix in {".parquet", ".pq"}:
        frame.to_parquet(path, index=False)
    elif suffix == ".json":
        frame.to_json(path, orient="records", indent=2)
    else:
        raise SystemExit("--predictions-out must end in .csv, .parquet, .pq, or .json")


def clipped_log_loss(y, p) -> float:
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


def json_value(value):
    if hasattr(value, "item"):
        value = value.item()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def mean_metrics(rows: list[dict], metric_names: list[str]) -> dict[str, float]:
    return {
        name: sum(float(row[name]) for row in rows) / len(rows)
        for name in metric_names
    }


def main() -> int:
    args = parse_args()
    if args.min_train_groups < 1:
        raise SystemExit("--min-train-groups must be at least 1")
    features = [c.strip() for c in args.features.split(",") if c.strip()]
    id_cols = [c.strip() for c in args.id_cols.split(",") if c.strip()]
    all_named_columns = [args.target, args.split_col, *features, *id_cols]
    if not features:
        raise SystemExit("--features must name at least one column")
    if len(set(all_named_columns)) != len(all_named_columns):
        raise SystemExit("target, split, feature, and identifier columns must not overlap")

    input_path = Path(args.input).resolve()
    output_paths = [Path(value).resolve() for value in [args.out, args.predictions_out] if value]
    if input_path in output_paths or len(output_paths) != len(set(output_paths)):
        raise SystemExit("input, fold artifact, and predictions output must be different files")
    if args.out and Path(args.out).suffix.lower() != ".json":
        raise SystemExit("--out must end in .json")

    df = load_frame(args.input)
    input_rows = int(len(df))
    required = all_named_columns
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    df = df[required].copy()
    df["source_row"] = df.index
    df = df.dropna(subset=[args.target, args.split_col, *features]).copy()
    rows_dropped_missing_required = input_rows - int(len(df))
    if df.empty:
        raise SystemExit("no complete modeling rows remain")
    if id_cols and (df[id_cols].isna().any().any() or df.duplicated(id_cols).any()):
        raise SystemExit("--id-cols must be non-null and jointly unique")
    if not set(df[args.target].unique()) <= {0, 1, False, True}:
        raise SystemExit(f"{args.target!r} must contain only 0/1 values")
    try:
        import numpy as np
        import pandas as pd
        from sklearn.linear_model import LogisticRegression
    except ImportError as exc:
        raise SystemExit(
            "numpy and scikit-learn are required; install them with: "
            "python -m pip install numpy scikit-learn"
        ) from exc
    numeric_features = df[features].apply(lambda column: pd.to_numeric(column, errors="coerce"))
    if numeric_features.isna().any().any() or not np.isfinite(numeric_features.to_numpy()).all():
        raise SystemExit("feature columns must contain only finite numeric values")
    df[features] = numeric_features

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
            f"({[json_value(g) for g in groups[args.min_train_groups:]]})"
        ),
        file=sys.stderr,
    )

    folds: list[dict] = []
    prediction_frames = []
    for index in range(args.min_train_groups, len(groups)):
        test_group = groups[index]
        train = df[df[args.split_col].isin(groups[:index])]
        test = df[df[args.split_col] == test_group]
        y_train = train[args.target].astype(int).to_numpy()
        y_test = test[args.target].astype(int).to_numpy()
        if len(np.unique(y_train)) < 2:
            raise SystemExit(f"training fold before {test_group!r} has only one target class")
        constant = np.full(len(test), y_train.mean())
        model = LogisticRegression(max_iter=2000, random_state=0).fit(train[features], y_train)
        pred = model.predict_proba(test[features])[:, 1]
        folds.append(
            {
                "fold": json_value(test_group),
                "n_train": int(len(train)),
                "n_test": int(len(test)),
                "constant_log_loss": clipped_log_loss(y_test, constant),
                "logistic_log_loss": clipped_log_loss(y_test, pred),
                "logistic_accuracy": float(((pred >= 0.5) == y_test).mean()),
            }
        )
        predictions = test[[*id_cols, "source_row", args.split_col]].copy()
        predictions["fold"] = json_value(test_group)
        predictions["y_true"] = y_test
        predictions["constant_probability"] = constant
        predictions["logistic_probability"] = pred
        # Portable handoff alias for calibration-check / reporting skills.
        predictions["p_pred"] = pred
        prediction_frames.append(predictions)

    fieldnames = list(folds[0])
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(folds)

    if args.out:
        metric_names = ["constant_log_loss", "logistic_log_loss", "logistic_accuracy"]
        artifact = {
            "artifact_type": "walk_forward_classification_metrics",
            "source": str(input_path),
            "target": args.target,
            "features": features,
            "split_col": args.split_col,
            "id_cols": id_cols or ["source_row"],
            "validation": {
                "design": "expanding_window",
                "min_train_groups": args.min_train_groups,
                "primary_metric": "log_loss",
            },
            "row_accounting": {
                "input_rows": input_rows,
                "modeling_rows": int(len(df)),
                "rows_dropped_missing_target_split_or_feature": rows_dropped_missing_required,
            },
            "preprocessing": {
                "missing_values": "complete-case rows shared by both baselines",
                "imputation": "none",
            },
            "models": ["training_rate_constant", "logistic_regression"],
            "folds": folds,
            "mean_metrics": mean_metrics(folds, metric_names),
        }
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    if args.predictions_out:
        write_predictions(pd.concat(prediction_frames, ignore_index=True), Path(args.predictions_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
