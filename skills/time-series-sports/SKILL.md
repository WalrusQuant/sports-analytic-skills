---
name: time-series-sports
description: Engineer and compare time-safe sports form features. Use for rolling windows, EWMA, rest, schedule gaps, early-season handling, and chronological evaluation.
license: MIT
metadata:
  version: "1.0.0"
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

Build shifted EWMA features on a user-owned event table, then compare already-computed feature sets on the same folds.

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

```bash
python -m pip install pandas numpy scikit-learn pyarrow
```

Build features in the user's environment. This repository does not ship a form-feature program.

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

## Feature construction

Require non-null entity keys, a parseable time or order field, and numeric or boolean values. Reject infinite values and contradictory event order. Leave missing observations missing. Do not fill them with zero. Shift each value by one event, then apply the rolling or EWMA summary.

Name generated fields so the shift is obvious, for example `pre_ewma_points`. Group by season when history should not cross the offseason; otherwise say that history carries across seasons. If `game_date` can tie, use `start_time` or another real event order. An arbitrary row id is not order.

### Opponent features

Compute each participant's history independently, then join the participant and
opponent snapshots by stable event/entity keys. Assert that both snapshots were
available before the event. Never derive opponent form from the focal row's
current result.

### Compare feature sets

Use identical expanding folds and the complete cases shared by both feature sets. Validate binary targets and finite numeric features, and do not impute them in the comparison. The comparison evaluates columns that already exist. It does not make an illegal feature legal.

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

On a team-game file, sort by `team_id` and `game_date`, shift the result, then take an EWMA. Compare that column with a shifted three-game mean under the same season folds before preferring either window.

```python
import pandas as pd
g = pd.read_parquet("team_games.parquet").sort_values(["team_id", "game_date"])
g["pre_points"] = g.groupby("team_id")["score"].shift(1)
g["pre_ewma_points"] = g.groupby("team_id")["pre_points"].transform(
    lambda s: s.ewm(span=5, min_periods=1).mean()
)
```

---

## Bundled Resources

### references/
| File | Contents |
|---|---|
| [form_feature_recipes.md](references/form_feature_recipes.md) | shift/roll/expand/EWMA recipes |
| [early_season.md](references/early_season.md) | small-sample handling |
| [rest_and_gaps.md](references/rest_and_gaps.md) | byes and calendar gaps |

## Related Skills

| Need | Skill |
|---|---|
| Feature legality | `feature-rules` |
| Ratings (opponent-adjusted) | `ratings-strength-models` |
| EDA | `eda-sports` |
| Models | `baseline-models`, `predictive-modeling` |
| Leakage | `leakage-audit` |

---
