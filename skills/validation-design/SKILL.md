---
name: validation-design
description: Design chronological sports-model validation and a written evaluation charter. Use for walk-forward splits, grouped time folds, metric locking, tuning boundaries, and go/no-go rules.
metadata:
  version: "0.12.0"
---

# Validation Design

## Outcome

Produce a written evaluation charter and fold table that simulate the real
prediction process. Sports data change through time—rosters, rules, tactics,
opponents, schedules, and collection systems—so random row splits are rarely an
honest default.

Read [the split patterns](references/split_patterns.md) while choosing fold
geometry, [the metric-lock guide](references/metrics_lock.md) before freezing
metrics, and [the anti-patterns](references/anti_patterns.md) during the final
design review.

## When to Use This Skill

Use when:

- locking folds, metrics, baselines, and go/no-go rules before fitting;
- replacing random K-fold with season or rolling-origin walk-forward;
- defining embargo/grouping for team-game panels or repeated events;
- the user asks how to validate a sports model honestly.

Do **not** use this skill as a substitute for:

- leakage review of the feature matrix → `leakage-audit`;
- fitting candidates after the charter is locked → `baseline-models` /
  `predictive-modeling`;
- probability reliability diagnostics → `calibration-check`.

| Need | Go instead |
|---|---|
| Feature legality | `feature-rules` |
| Leakage verdict | `leakage-audit` |
| Baseline ladder | `baseline-models` |

## Charter: lock before fitting

Record:

- question, target, row grain, prediction decision time T, and eligible population;
- chronological split unit and unambiguous ordering;
- grouping for paired perspectives, repeated events, entities, seasons, or series;
- minimum training history; expanding or sliding window and why;
- gap/embargo tied to label or source finalization;
- primary metric, secondary diagnostics, baselines, and practical success rule;
- tuning boundary, early-stopping data, and final untouched holdout;
- leakage checks, fold reporting, failure conditions, and allowed reruns.

If the charter changes after results, create a new evaluation version and label
the prior result exploratory.

## Default protocol

1. Order observations by the time information becomes usable, not file order.
2. Keep training strictly before testing, including publication delay and embargo.
3. Choose one primary metric and baselines before fitting candidates.
4. Use season/competition walk-forward when blocks have enough events.
5. Use finer rolling-origin folds for frequent predictions when season blocks are too coarse.
6. Fit every transform and tune every hyperparameter using past training data only.
7. Score each outer test fold once for a fixed candidate.
8. Report fold-level results, dispersion, failures, and baseline gaps—not only pooled means.
9. Preserve a final holdout until feature families and candidates are frozen.

## Split patterns

### Season walk-forward

```text
train through 2020 -> test 2021
train through 2021 -> test 2022
train through 2022 -> test 2023
```

This is a strong default for season-based leagues. Each test season must have
enough eligible rows and prior seasons must satisfy the minimum-history rule.

### Expanding versus sliding

| Window | Training data | Prefer when |
|---|---|---|
| Expanding | all eligible history before test | stable process; scarce data |
| Sliding | most recent K blocks | documented regime drift/rule change |

Select K without optimizing on the final holdout. Report how many rows/entities
each window discards.

### Rolling origin inside a season

```text
train through week 6 -> test week 7
train through week 7 -> test week 8
```

Use for high-frequency labels or operational retraining. Features still require
shift/as-of construction; a time split cannot repair a leaky matrix.

### Embargo and availability gap

If labels settle or sources publish after an event, the last training event may
not be usable immediately. Set the gap from the actual maximum availability
delay, not an arbitrary number. Document whether postponed events and revisions
extend the gap.

### Grouping and panels

A team-game panel commonly has two rows per contest. Keep related perspectives
in the same fold and avoid presenting doubled team-row accuracy as independent
game-pick accuracy. Player-event rows may share lineup, game, or series effects;
choose grouping based on the claim. Entity grouping must not accidentally place
future rows into training when chronology is primary.

### Nested tuning

```text
Outer test block S
  Inner chronological folds inside blocks < S choose configuration
  Refit chosen configuration on all eligible data < S
  Score S once
```

Early stopping is tuning. It needs an inner training-period validation slice,
not the outer test fold.

## Metric lock

| Task | Primary candidate | Secondary diagnostics |
|---|---|---|
| Win probability | log-loss | Brier, calibration/ECE, accuracy |
| Margin/value | MAE | RMSE, bias, residual slices |
| Counts/rates | deviance or MAE | rate calibration, zero behavior |
| Ranking | future-period Spearman | pairwise accuracy, stability |

Accuracy alone ignores probability quality. RMSE weights large misses more than
MAE. Pick based on decision loss and target semantics, then specify direction,
aggregation, weighting, missing predictions, and tie behavior.

Every candidate needs naive and domain-relevant baselines under identical rows
and folds: constant training rate/mean, home indicator, last-value/rating, or
another simple legal comparator.

## Fold construction diagnostics

```python
for fold in folds:
    train = df.loc[fold.train]
    test = df.loc[fold.test]
    assert train["event_time"].max() < test["event_time"].min()
    assert set(train["game_id"]).isdisjoint(set(test["game_id"]))
```

For each fold record train/test period, row count, event count, entity count,
target base rate, excluded rows, availability gap, and required-column nulls.
Inspect whether one shortened season, expansion era, postseason, or source
change dominates results.

## Standalone helpers

Print expanding walk-forward fold sizes from user-owned CSV, Parquet, JSON,
JSONL, or NDJSON. The helper requires `pandas`, validates every named column,
sorts distinct split values, and accepts any ordered season/date/group column.

```bash
python /path/to/validation-design/scripts/print_folds.py \
  --input modeling_table.csv --split-col season \
  --required-cols won,is_home,rating_diff --min-train-groups 2

python /path/to/validation-design/scripts/write_charter.py \
  --out data/validation_charter.md
```

**`--min-train-groups` default is 2.** That means the first N groups are
training-only history and never appear as a test fold. Example with seasons
`2022, 2023, 2024`:

- default `2` → one test fold: 2024 (train 2022+2023)
- `1` → test folds: 2023 and 2024

The helper prints the planned test folds on stderr before the CSV table. Match
this setting when calling `baseline-models` / `predictive-modeling` helpers so
evaluation rows stay identical.

The helper exposes row counts for expanding group folds; it does not verify T,
dependency grouping, embargo, transform fitting, or tuning isolation. Verify
those manually before calling the design valid. Supported ordering values are
finite numbers, ISO dates/timestamps, and common consecutive season ranges such
as `2022-23`, `2022/23`, or `2022-2023`. Other labels—including stages whose
lexical order is not chronology—require an explicit numeric ordinal/date field.
The output is CSV with one row per test group.

## Anti-patterns

| Anti-pattern | Why it fails | Repair |
|---|---|---|
| random K-fold on events | future structure enters training | forward-only folds |
| full-data scaler/imputer | test distribution leaks | fold-local pipeline |
| early stopping on outer test | test becomes tuning data | inner validation slice |
| repeated final-holdout checks | adaptive overfitting | freeze and score once |
| dropping an ugly fold | selection bias | report it; explain regime |
| reporting pooled mean only | instability is hidden | per-fold table + dispersion |
| no baseline | metric lacks context | score legal baselines identically |
| different rows per candidate | unfair comparison | common eligible sample/disclose |
| team rows called game accuracy | paired rows double-count | home-only or game aggregation |

## Reporting table and decision

```text
fold | train_period | test_period | train_n | test_n | baseline_primary |
candidate_primary | gap | secondary_metrics | exclusions | failures
```

Report mean and spread across folds, but preserve each fold. Weighting folds by
rows answers a different question than equal-fold averaging; declare which is
primary. Include calibration and relevant regime/entity slices when claims rely
on them. The success rule should combine the locked primary metric, baseline
gap, meaningful fold consistency, and non-negotiable leakage/calibration limits.

## Charter template

```text
Validation charter
Target / grain / decision time T / eligible population:
Split unit and ordering:
Grouping rule:
Minimum training history:
Window: expanding | sliding(K=)
Gap/embargo and availability rationale:
Primary metric definition:
Secondary diagnostics:
Baselines:
Inner tuning and early stopping:
Final untouched holdout:
Common evaluation rows:
Success / failure rule:
Required leakage checks:
Per-fold reporting and slice requirements:
Allowed reruns / versioning:
```

## Worked example and integrity rules

For team-game win probability: set T to kickoff, group both perspectives by
game, walk forward by season with two prior seasons, fit preprocessing and tune
inside each outer training set, use log-loss as primary with Brier/calibration
secondary, compare constant-rate and home-indicator baselines, and report every
season. Use one perspective or game aggregation for game-level claims.

1. No row, dependency group, transform fit, or tuning signal crosses future to past.
2. Lock metrics and success before candidates; publish ugly folds.
3. Keep the final holdout untouched until candidates and features are frozen.
4. Use `references/split_patterns.md` for designs,
   `references/metrics_lock.md` for metrics, and
   `references/anti_patterns.md` for review.
5. Pair with `feature-rules` and `leakage-audit`; clean folds cannot repair unsafe features.
