---
name: time-series-sports
description: Engineer and compare time-safe sports form features. Use for rolling windows, EWMA, rest, schedule gaps, early-season handling, and chronological evaluation.
metadata:
  version: "0.12.0"
---

# Time-Series Sports Features

Sports observations are ordered and dependent. Build each feature as if replaying history at the prediction decision time.

## Time-safe construction

- Sort by entity and event time with deterministic tie breaking.
- Shift the raw event value before rolling, expanding, or EWMA aggregation.
- Decide explicitly whether history resets by season, competition, roster era, or never.
- Keep the window unit clear: games, days, possessions, plate appearances, or minutes.
- Carry forward only information genuinely available at the decision time.
- Model early-history missingness deliberately; do not backfill from future events.
- Generate opponent features independently and join them by event/entity keys with point-in-time checks.

Read [references/form_feature_recipes.md](references/form_feature_recipes.md) for rolling recipes, [references/early_season.md](references/early_season.md) for priors and missingness, and [references/rest_and_gaps.md](references/rest_and_gaps.md) for schedule features.

## Bundled helpers

`ewma_form.py` reads a user-owned CSV, Parquet, JSON, JSONL, or NDJSON event table, validates the entity/time/value columns, shifts values by one event within each group, and writes CSV or Parquet. It requires pandas.

```bash
python /path/to/time-series-sports/scripts/ewma_form.py \
  --input team_games.csv --entity-col team --time-col event_time \
  --order-col event_sequence \
  --group-cols season --values won,point_margin --span 5 \
  --out team_games_with_ewma.csv
```

The generated names are `pre_ewma_<value>`. Omitting `--group-cols` carries
history across the full entity timeline. The event order must be unique within
each entity/reset group. If `--time-col` can tie, provide a genuinely
chronological `--order-col`; a row identifier that does not encode event order
is not sufficient.

Compare any two already-computed feature sets on identical chronological folds:

```bash
python /path/to/time-series-sports/scripts/compare_form_windows.py \
  --input modeling_table.csv --target won --split-col season \
  --features-a pre_roll3_win,pre_roll3_margin \
  --features-b pre_ewma_won,pre_ewma_point_margin
```

The comparison requires pandas, NumPy, and scikit-learn. Replace `/path/to/time-series-sports` with the installed skill path.
