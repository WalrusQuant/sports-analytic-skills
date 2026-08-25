---
name: time-series-sports
description: Engineer and compare time-safe sports form features. Use for rolling windows, EWMA, rest, schedule gaps, early-season handling, and chronological evaluation.
metadata:
  version: "0.12.0"
---

# Time Series & Form (Sports)

## Overview

Sports performance is ordered in time. This skill builds **form features** and
simple trajectory forecasts that are legal at decision time T:

- rolling means
- expanding rates
- EWMA / decay
- rest gaps
- regime flags

The bundled helper constructs shifted EWMA features from a user-owned event
table, and the comparison helper evaluates already-computed feature sets.

**Non-negotiable:** shift (or as-of) so the current game is never inside the feature.

---

## When to Use This Skill

Use when:

- Team/player form features for pre-game models
- Rolling averages, EWMA, half-life decay
- Forecasting next-game stats from trajectories
- Handling bye weeks, missing games, season breaks
- Comparing recency-weighted form vs static season averages
- User says “hot streak,” “last 5,” or “recent form”

Do **not** use when:

| Need | Go instead |
|---|---|
| Pure cross-sectional comparison with no recency | EDA / stats skills |
| Opponent-adjusted strength is the real goal | also `ratings-strength-models` |
| Static season aggregates already sufficient and time-safe | simpler baselines |
| Feature legality review of a finished matrix | `leakage-audit` |

---

## Installation

`ewma_form.py` requires pandas. `compare_form_windows.py` additionally
requires NumPy and scikit-learn:

```bash
python -m pip install pandas numpy scikit-learn
```

Parquet input also needs `pyarrow` or `fastparquet`.

---

## Workflow

1. Define the **entity** and **frequency** (team-game, player-game, week).
2. Sort by entity + time; handle missing games explicitly.
3. Choose window/decay rules; tune only inside training folds.
4. Apply **`shift(1)` / as-of** so current game is never inside the feature.
5. Compare form features against static baselines under walk-forward validation.
6. Watch early-season small-sample explosions — min-games thresholds or shrinkage.
7. Document window/span, shift rule, and min history.
8. Hand off to baselines / predictive models / leakage audit.

---

## Core Techniques

| Technique | Sports use | Time-safety rule |
|---|---|---|
| Expanding mean | season-to-date win % / PF | shift before expand |
| Rolling mean | last K games form | shift then rolling |
| EWMA | recency-weighted form | ewm on shifted series |
| Rest days | schedule gaps | diff of game dates |
| Season phase | week number, month | known pre-game |
| Regime split | rule changes, coaching eras | flag by date known at T |

Read [form_feature_recipes.md](references/form_feature_recipes.md) when implementing rolling, expanding,
or EWMA features. Read [early_season.md](references/early_season.md) when choosing priors,
minimum history, or shrinkage. Read [rest_and_gaps.md](references/rest_and_gaps.md) for byes,
calendar gaps, and elapsed-time features.

---

## Standalone Feature Construction

`ewma_form.py` requires non-null entity/reset keys, parseable finite numeric or
timestamp time/order fields, and numeric or boolean value dtypes (including
pandas nullable numeric/boolean dtypes). It rejects infinite values and contradictory
event ordering. Missing observations in value columns remain missing—they are
never filled with zero—before each value is shifted by one event and summarized
with pandas EWMA semantics.

```bash
python /path/to/time-series-sports/scripts/ewma_form.py \
  --input team_games.csv --entity-col team --time-col event_time \
  --order-col event_sequence --group-cols season \
  --values won,point_margin --span 5 \
  --out team_games_with_ewma.csv
```

Generated fields are named `pre_ewma_<value>`. Omitting `--group-cols`
carries history across the full entity timeline. If `--time-col` can tie,
`--order-col` must encode genuine event order; an arbitrary row ID is not
enough.

### Opponent features

Compute each participant's history independently, then join the participant and
opponent snapshots by stable event/entity keys. Assert that both snapshots were
available before the event. Never derive opponent form from the focal row's
current result.

### Compare feature sets

```bash
python /path/to/time-series-sports/scripts/compare_form_windows.py \
  --input modeling_table.csv --target won --split-col season \
  --features-a pre_roll3_win,pre_roll3_margin \
  --features-b pre_ewma_won,pre_ewma_point_margin
```

The comparison uses identical expanding folds and complete cases shared by both
feature sets. It validates binary targets and finite numeric features, but does
not impute them. It evaluates hypotheses already encoded in the supplied
columns; it does not make illegal features legal.

## Early-Season Handling

| Problem | Mitigation |
|---|---|
| Week 1 empty history | NA features + drop or league prior |
| Tiny n rolling windows | require `pre_games_played >= k` |
| Noisy short rolls | shrinkage toward league mean / expanding mean |
| Bye weeks | rest_days feature; don’t fill with zeros blindly |
| Offseason gaps | don’t treat long rest as a normal short-week rest without care |

---

## Validation

Form features are hypotheses. Evaluate alternative windows on identical
chronological folds, against a static or simpler baseline.

Tune window/span **inside training folds only**.

---

## Hard Constraints

1. No centered rolling windows that peek forward.
2. No “season average including current game.”
3. Early-season priors/shrinkage when n is tiny.
4. Validate across seasons, not one hot streak.
5. Opponent strength still matters — raw form ≠ opponent-adjusted strength (`ratings-strength-models`).
6. Document shift rule in every feature card / experiment log.

---

## Anti-Patterns

- Fixed 5-game mean with no shrinkage
- Ignoring opponent strength in raw form
- Treating playoffs and regular season as identical without a flag
- Tuning window length on the final test season only
- Filling NA form with 0.0 silently
- Claiming “hot streak” causality from one rolling mean

---

## Reporting Template

```text
Form model: rolling / EWMA / expanding
Entity/frequency:
Windows/span:
Shift rule: shift(1) before aggregate
Min history:
Validation: vs static baseline under walk-forward
Limits: early season, injuries, opponent strength…
Reproduce:
```

---

## Output Contract

Done means:

- [ ] Entity/frequency stated
- [ ] Shift/as-of rule stated
- [ ] Window/span documented
- [ ] Min history rule stated
- [ ] Walk-forward comparison planned or done
- [ ] Leakage check planned or done

---

## Worked Example

```bash
python /path/to/time-series-sports/scripts/ewma_form.py \
  --input team_games.csv --entity-col team --time-col event_time \
  --order-col event_sequence --group-cols season \
  --values won,point_margin --span 5 \
  --out team_games_with_ewma.csv

python /path/to/time-series-sports/scripts/compare_form_windows.py \
  --input modeling_table.csv --target won --split-col season \
  --features-a pre_roll3_win,pre_roll3_margin \
  --features-b pre_ewma_won,pre_ewma_point_margin
```

---

## Bundled Resources

### references/
| File | Contents |
|---|---|
| [form_feature_recipes.md](references/form_feature_recipes.md) | shift/roll/expand/EWMA recipes |
| [early_season.md](references/early_season.md) | small-sample handling |
| [rest_and_gaps.md](references/rest_and_gaps.md) | byes and calendar gaps |

### scripts/
| File | Contents |
|---|---|
| `ewma_form.py` | shifted EWMA form table |
| `compare_form_windows.py` | walk-forward compare roll vs EWMA features |


---

## Related Skills

| Need | Skill |
|---|---|
| Feature legality | `feature-rules` |
| Ratings (opponent-adjusted) | `ratings-strength-models` |
| EDA | `eda-sports` |
| Models | `baseline-models`, `predictive-modeling` |
| Leakage | `leakage-audit` |

---

## Quick Command Card

```bash
python /path/to/time-series-sports/scripts/ewma_form.py \
  --input team_games.csv --entity-col team --time-col event_time \
  --order-col event_sequence --group-cols season \
  --values won,point_margin --span 5 \
  --out team_games_with_ewma.csv

python /path/to/time-series-sports/scripts/compare_form_windows.py \
  --input modeling_table.csv --target won --split-col season \
  --features-a pre_roll3_win,pre_roll3_margin \
  --features-b pre_ewma_won,pre_ewma_point_margin
```

---
