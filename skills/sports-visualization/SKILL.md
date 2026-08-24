---
name: sports-visualization
description: >
  Create honest sports-analysis figures from user-owned data, including
  distributions, rates, rating trajectories, calibration plots, and
  walk-forward metric comparisons. Use for exploration and communication.
license: MIT
metadata:
  version: "0.7.0"
---

# Sports Visualization

Every important figure should state its period, sample size, metric definition,
grain, and relevant baseline. Plot uncertainty when the claim depends on noisy
differences. Do not use chart decoration as evidence.

## Workflow

1. Define the question and the unit represented by each mark.
2. Validate the input grain and columns.
3. Choose the smallest chart that answers the question.
4. Add denominators, time range, and comparison baseline.
5. Check axis ranges, aggregation, missingness, and duplicated events.
6. Export reproducibly and write a one-sentence interpretation with limits.

See `references/plot_catalog.md` for chart selection and
`references/honest_labels.md` for labeling rules.

## Standalone helpers

Install `pandas` and `matplotlib`; Parquet also needs `pyarrow` or `fastparquet`.
The table helpers accept user-owned CSV, Parquet, JSON, JSONL, or NDJSON.

For a team-game panel with `is_home` and `point_diff`:

```bash
python /absolute/path/to/plot_home_margin_hist.py \
  --input games.csv --out home_margin.png
```

For a panel with `season`, `is_home`, and binary `won`:

```bash
python /absolute/path/to/plot_home_win_rate.py \
  --input games.parquet --out home_rate.png
```

Column flags map alternate schemas. Both commands validate required columns.

For a JSON report containing a `folds` array, each row must contain an explicit
fold label plus the named candidate and baseline metric fields:

```bash
python /absolute/path/to/plot_walkforward_metrics.py \
  --json metrics.json --fold-col fold --metric logistic_log_loss \
  --baseline constant_log_loss --out comparison.png
```

Do not label training metrics as validation results. When a chart compares
models, ensure all bars use the same events and folds.
