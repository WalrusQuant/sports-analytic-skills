---
name: eda-sports
description: >
  Exploratory data analysis for user-provided sports data: grain, key integrity,
  coverage, missingness, entity balance, base rates, outliers, structural breaks,
  and leakage red flags. Use before feature engineering or model fitting.
license: MIT
metadata:
  version: "0.12.0"
---

# EDA for Sports Data

Start with the question and prediction timestamp, then establish what one row
means. Never interpret summary statistics until grain and keys are verified.

## Workflow

1. State the expected grain: game, team-game, player-game, play, or event.
2. Test primary-key uniqueness and inspect duplicates.
3. Measure season/period and team/player coverage.
4. Measure missingness overall and by season or source.
5. Inspect targets, scores, margins, and relevant subgroups.
6. Look for structural breaks caused by rules, schedules, or collection changes.
7. Flag every field unavailable at the intended prediction timestamp.
8. Finish with a go, repair, or stop recommendation.

Read `references/grain_guide.md`, `references/eda_checklist.md`, and
`references/red_flags.md` when the corresponding issue is in scope.

## Standalone helpers

The helpers read user-owned CSV, Parquet, JSON, JSONL, or NDJSON files. They use
only public Python packages. Install `pandas`; Parquet also needs `pyarrow` or
`fastparquet`.

`scripts/coverage_table.py` expects a team-game panel with `season`, `week`,
`game_id`, and `team`. Rename these through its column flags.

```bash
python /absolute/path/to/coverage_table.py --input games.csv
```

`scripts/panel_report.py` expects `season`, `game_id`, `team`, `is_home`, and
binary `won`, with column-name flags for alternate schemas.

```bash
python /absolute/path/to/panel_report.py --input games.parquet --out eda.json
```

Do not silently guess columns. If a required field is unavailable, explain the
schema mismatch and stop or create an explicit, reviewed mapping.

## Reporting

Record source, extraction date, grain, keys, coverage, missingness, target base
rate, suspicious columns, repairs performed, and remaining limitations. A clean
EDA report does not certify that engineered features are time-safe.
