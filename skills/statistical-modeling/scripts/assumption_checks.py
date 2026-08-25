#!/usr/bin/env python3
"""Check normality, outliers, and optional group variance in a data column."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_table(path: Path):
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit("This command requires pandas. Install it with: pip install pandas") from exc
    if path.suffix.lower() == ".csv": return pd.read_csv(path)
    if path.suffix.lower() in {".parquet", ".pq"}: return pd.read_parquet(path)
    if path.suffix.lower() in {".json", ".jsonl", ".ndjson"}: return pd.read_json(path, lines=path.suffix.lower() != ".json")
    raise SystemExit("--input must be CSV, Parquet, JSON, JSONL, or NDJSON")


def check_normality(data, alpha: float = 0.05) -> dict:
    import numpy as np
    from scipy import stats
    values = np.asarray(data, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < 3: raise ValueError("normality check requires at least three values")
    # Shapiro is most useful on moderate samples; cap deterministically for very large data.
    tested = values[:5000]
    statistic, p_value = stats.shapiro(tested)
    return {"test": "Shapiro-Wilk", "n": len(values), "n_tested": len(tested), "statistic": float(statistic), "p_value": float(p_value), "passes_at_alpha": bool(p_value > alpha)}


def detect_outliers(data, threshold: float = 1.5) -> dict:
    import numpy as np
    values = np.asarray(data, dtype=float)
    values = values[np.isfinite(values)]
    if not len(values): raise ValueError("outlier check requires at least one value")
    q1, q3 = np.percentile(values, [25, 75]); iqr = q3 - q1
    lower, upper = q1 - threshold * iqr, q3 + threshold * iqr
    mask = (values < lower) | (values > upper)
    return {"method": "IQR", "threshold": threshold, "lower_bound": float(lower), "upper_bound": float(upper), "n_outliers": int(mask.sum()), "pct_outliers": float(mask.mean() * 100)}


def check_homogeneity_of_variance(frame, value_col: str, group_col: str, alpha: float = 0.05) -> dict:
    import numpy as np
    from scipy import stats
    groups = [group[value_col].dropna().to_numpy(dtype=float) for _, group in frame.groupby(group_col)]
    groups = [group for group in groups if len(group) >= 2]
    if len(groups) < 2: raise ValueError("variance check requires at least two groups with two observations each")
    statistic, p_value = stats.levene(*groups, center="median")
    variances = [np.var(group, ddof=1) for group in groups]
    has_zero_variance = any(value == 0 for value in variances)
    ratio = max(variances) / min(variances) if variances and not has_zero_variance else None
    return {"test": "Levene (median centered)", "groups": len(groups), "statistic": float(statistic), "p_value": float(p_value), "passes_at_alpha": bool(p_value > alpha), "variance_ratio": float(ratio) if ratio is not None else None, "variance_ratio_status": "undefined_zero_variance" if has_zero_variance else "defined"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--value-col", required=True)
    parser.add_argument("--group-col", default="")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--outlier-threshold", type=float, default=1.5)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not 0 < args.alpha < 1:
        parser.error("--alpha must be between 0 and 1")
    if args.outlier_threshold <= 0:
        parser.error("--outlier-threshold must be greater than 0")
    try:
        import scipy  # noqa: F401
        import numpy  # noqa: F401
    except ImportError as exc:
        raise SystemExit("This command requires numpy and scipy. Install them with: pip install numpy scipy") from exc
    frame = load_table(args.input)
    required = [args.value_col] + ([args.group_col] if args.group_col else [])
    missing = [column for column in required if column not in frame.columns]
    if missing: raise SystemExit(f"missing required columns: {', '.join(missing)}")
    import numpy as np
    import pandas as pd

    numeric = pd.to_numeric(frame[args.value_col], errors="coerce")
    invalid = frame[args.value_col].notna() & numeric.isna()
    if invalid.any():
        raise SystemExit(f"{args.value_col!r} must contain numeric values")
    if np.isinf(numeric.dropna().to_numpy(dtype=float)).any():
        raise SystemExit(f"{args.value_col!r} must not contain infinite values")
    frame[args.value_col] = numeric
    analyzed_rows = int(frame[args.value_col].notna().sum())
    if analyzed_rows < 3:
        raise SystemExit("normality check requires at least three finite non-null values")
    report = {
        "source": str(args.input), "value_column": args.value_col, "alpha": args.alpha,
        "row_accounting": {
            "input_rows": int(len(frame)),
            "analyzed_value_rows": analyzed_rows,
            "rows_missing_value": int(frame[args.value_col].isna().sum()),
        },
        "normality": check_normality(frame[args.value_col].dropna(), args.alpha),
        "outliers": detect_outliers(frame[args.value_col].dropna(), args.outlier_threshold),
    }
    if args.group_col:
        try:
            report["homogeneity"] = check_homogeneity_of_variance(
                frame, args.value_col, args.group_col, args.alpha
            )
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2)); print(f"wrote {args.out}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
