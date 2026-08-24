---
name: feature-rules
description: Define, review, and document point-in-time legal sports-model features. Use when creating rolling form, rest, matchup, rating, roster, injury, or contextual predictors.
---

# Feature Rules

Every feature needs an explicit prediction decision time. A feature is legal only if its raw sources and every transformation would have been available at that time for the historical row.

## Rules

- Shift outcomes before rolling, expanding, or exponentially weighted aggregation.
- Use as-of joins with publication timestamps, not merely event dates.
- Fit imputers, encoders, scaling, selection, and dimensionality reduction inside each training fold.
- Keep current-event scores, outcomes, and post-event corrections out of pre-event features.
- Distinguish scheduled information from later revised information.
- Record source, grain, availability time, lookback, shift, null policy, and expected early-history behavior for each feature.

Use [references/feature_card_template.md](references/feature_card_template.md) to document features, [references/legality_matrix.md](references/legality_matrix.md) for common source types, and [references/shift_patterns.md](references/shift_patterns.md) for time-safe transformations.

## Bundled helpers

Both helpers inspect a user-owned CSV, Parquet, JSON, JSONL, or NDJSON table and require pandas. Candidate features are always explicit; there is no hidden model feature list.

```bash
python /path/to/feature-rules/scripts/feature_preview.py \
  --input features.csv --features pre_win_rate,rest_days,rating_diff \
  --context season,event_id,team

python /path/to/feature-rules/scripts/legality_report.py \
  --input feature_catalog.csv --features pre_win_rate,rest_days,rating_diff \
  --available-at-col availability --out feature_legality.json
```

For `--available-at-col`, accepted timing labels are `pregame`, `pre-game`, `pre_decision`, `pre-decision`, and `before`. A passing automated report is only a candidate verdict; verify source timestamps and transformation code manually. Replace `/path/to/feature-rules` with the installed skill path.

## Hard constraints

- Unknown availability is not a pass.
- A shift does not repair a source that was itself published after decision time.
- Fold-fitted preprocessing is part of feature legality.

## Output contract

Produce a feature inventory with source, grain, availability time, transform,
lookback, shift, missing-value behavior, legality verdict, evidence, and required
remediation.
