---
name: ratings-strength-models
description: >
  Build and evaluate sports strength models, including sequential Elo ratings,
  offense/defense splits, power ratings, and strict pre-event matchup features.
  Use for rankings, opponent adjustment, and strong prediction baselines.
license: MIT
metadata:
  version: "0.7.0"
---

# Ratings and Strength Models

The non-negotiable rule is as-of correctness: the rating attached to an event
must be the rating that existed before that event.

## Workflow

1. Choose the result signal: win, margin, score ratio, or domain-specific value.
2. Choose sequential updates or a batch model appropriate to the question.
3. Define initialization, home advantage, update size, and season carryover.
4. Sort events deterministically and save pre-event ratings before updating.
5. Convert rating differences to matchup predictions.
6. Evaluate by future time blocks against simple constant and home baselines.
7. Perform sensitivity checks rather than selecting parameters on test seasons.
8. Report parameters, ordering, carryover, metrics, and limitations.

Read `references/rating_families.md`, `references/parameters.md`, and
`references/evaluation.md` for model choice and validation detail.

## Standalone Elo builder

Install `pandas`; Parquet input also needs `pyarrow` or `fastparquet`.
`scripts/elo_asof.py` reads user-owned CSV, Parquet, JSON, JSONL, or NDJSON with
one row per completed game. Defaults require:

- `season`, `game_date`, and unique `game_id`
- `home_team`, `away_team`, `home_score`, and `away_score`

Every name is configurable. `game_date` may instead be any deterministic,
sortable event-order field.

```bash
python /absolute/path/to/elo_asof.py \
  --input games.csv --out elo_asof.csv --k 20 --home-adv 65
```

The output has two rows per game and includes `team`, `opponent`, `is_home`,
`elo_pre`, raw `rating_diff`, home-adjusted `elo_diff`,
`win_probability`, and `actual`. Ratings update only after both pre-event
rows are saved. Ties receive an outcome value of `0.5`. The order field must
strictly order every team's games; use kickoff timestamps or a verified event
sequence when dates can tie.

Evaluate the output without any private package:

```bash
python /absolute/path/to/eval_elo_baseline.py --input elo_asof.csv
```

The evaluator scores home rows once per game and reports season log loss, Brier
score, accuracy, and the constant 0.5 log-loss reference.

## Method limits

Elo is path-dependent and its scale is conventional. Rankings are not causal,
do not automatically account for roster changes, and can lag abrupt changes.
