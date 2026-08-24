---
name: validation-design
description: Design chronological sports-model validation and a written evaluation charter. Use for walk-forward splits, grouped time folds, metric locking, tuning boundaries, and go/no-go rules.
---

# Validation Design

Choose validation from the real prediction process, not convenience. Sports models normally require forward-only evaluation because rosters, rules, opponents, and data-generating conditions change over time.

## Charter

Record before modeling:

- target, row grain, and prediction decision time;
- eligible population;
- chronological split unit and embargo/gap if needed;
- minimum training history and expanding versus sliding window;
- how related rows are grouped;
- primary and secondary metrics;
- baselines and practical success threshold;
- tuning boundary and final untouched holdout;
- leakage checks and reporting format.

Prefer season or competition walk-forward when each group provides enough events. Use finer rolling-origin folds for frequent predictions, while keeping repeated entities and paired perspectives from crossing boundaries incorrectly. All preprocessing and tuning belong inside past data only.

Read [references/split_patterns.md](references/split_patterns.md) for fold shapes, [references/anti_patterns.md](references/anti_patterns.md) for common errors, and [references/metrics_lock.md](references/metrics_lock.md) before freezing evaluation criteria.

## Bundled helpers

Print expanding walk-forward fold sizes from a user-owned CSV, Parquet, JSON, JSONL, or NDJSON table:

```bash
python /path/to/validation-design/scripts/print_folds.py \
  --input modeling_table.csv --split-col season \
  --required-cols won,is_home,rating_diff --min-train-groups 2
```

The fold helper requires pandas, validates every named column, sorts distinct split values, and never imports optional libraries before parsing arguments.

Create an editable validation charter:

```bash
python /path/to/validation-design/scripts/write_charter.py --out validation_charter.md
```

Replace `/path/to/validation-design` with the installed skill path. Do not report only pooled metrics: include each fold's time range, sample size, primary metric, baseline gap, and failures.

## Hard constraints

- No row, entity group, transform fit, or tuning signal may cross from future to past.
- Split labels must have an unambiguous numeric or chronological order.
- The final holdout remains untouched until the design and candidates are frozen.

## Output contract

Produce a written charter plus a fold table containing train/test periods,
sample sizes, grouping rules, gaps/embargoes, primary and secondary metrics,
baselines, tuning boundary, success threshold, and failure conditions.
