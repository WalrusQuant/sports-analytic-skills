---
name: feature-rules
description: >
  Build time-safe sports features for pre-game modeling — as-of joins, shifted
  rolling and expanding form, opponent differentials, rest features, legality
  labels, and min-history thresholds. Use when creating feature matrices for
  wins/margins/player stats or reviewing whether features could know the future.
  Includes sports_ds.team_form builders, preview scripts, and a legality matrix.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# Feature Rules for Sports

## Overview

A feature is legal for prediction at time **T** only if it would have been
knowable at T from published information.

This skill defines:

- the legality test
- feature families (legal / illegal / conditional)
- the `sports_ds` pre-game team form builder
- procedures for rest, opponent joins, and min-history filters
- anti-patterns and checks

---

## When to Use This Skill

Use when:

- Building pre-game team/player features
- Reviewing a feature matrix for look-ahead
- Extending form windows, rest features, rating differentials
- User says “add features,” “rolling average,” or “is this leaky?”

Do **not** use as a substitute for:

| Need | Go to |
|---|---|
| EDA first | `eda-sports` |
| Full adversarial leakage audit | `leakage-audit` |
| Ratings as the feature system | `ratings-strength-models` |
| EWMA form detail | `time-series-sports` |

---

## Installation

```bash
pip install -e .
```

---

## Legality Test

For every feature, answer:

> At prediction time T, could an analyst know this value from published info at or before T?

| Answer | Action |
|---|---|
| Yes | legal |
| Only with delay | shift by the delay |
| No | illegal for this T |
| Partially | encode only the known portion |

Write T in plain language (e.g. “scheduled kickoff,” “first pitch,” “lineup lock”).

---

## Workflow

1. **Declare T** and target.
2. List raw fields and when each becomes known.
3. Build features with `shift(1)` / as-of joins only.
4. Label each feature legal / illegal / conditional.
5. Drop illegal features.
6. Set min history thresholds (`pre_games_played >= n`).
7. Preview null rates and heads.
8. Hand off to baselines/models under walk-forward validation.
9. Run leakage smoke / audit scripts.

```bash
python skills/feature-rules/scripts/feature_preview.py --seasons 2023-2024
python skills/feature-rules/scripts/legality_report.py --seasons 2023-2024
python skills/predictive-modeling/scripts/leakage_smoke.py
python skills/leakage-audit/scripts/audit_pregame_features.py --seasons 2023-2024
```

---

## Implemented Builder: pre-game team form

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features

panel = load_team_game_panel([2022, 2023, 2024])
feat = add_pregame_form_features(panel, windows=[3, 5])
```

### What it creates

**Team prior form (shifted):**

- `pre_win_pct`, `pre_avg_pf`, `pre_avg_pa`, `pre_avg_diff`
- `pre_games_played`
- `roll{W}_win_pct`, `roll{W}_diff` for each window W

**Opponent mirrors:**

- `opp_pre_win_pct`, `opp_pre_avg_diff`, `opp_pre_games_played`
- `opp_roll3_*`, `opp_roll5_*`

**Model differentials:**

- `feature_win_pct_diff`
- `feature_diff_diff`
- `feature_roll3_win_diff`
- `feature_roll5_diff_diff`

### Implementation rule

All group operations use **`shift(1)` before expanding/rolling**.

Code: `src/sports_ds/features/team_form.py`

Pipeline feature list: `sports_ds.pipelines.nfl_win_model.FEATURE_COLS`

---

## Feature Families

### Usually legal if as-of T

- prior-game aggregates ending before T
- schedule context (home/away, rest days from known schedule)
- ratings computed only from past games (`ratings-strength-models`)
- market prices only if timestamped at/before T (optional; not required for core DS)

### Illegal for pre-game T

- current game points / yards / EPA / won
- final season averages applied to early weeks
- opponent season totals that include this matchup
- post-game injury/participation without timestamp used as pre-game availability
- target encoding fit on full dataset including future rows

### Conditional

| Feature idea | Condition |
|---|---|
| Injury reports | timestamped source at/before T |
| In-game live features | only if T is in-game |
| Opening line | only with timestamp ≤ T |
| Weather | forecast available at T, not final observed if post-game |

See `references/legality_matrix.md`.

---

## Construction Patterns

### Shift then roll (required)

```python
# CORRECT
s.shift(1).rolling(5, min_periods=1).mean()

# WRONG — includes current game
s.rolling(5, min_periods=1).mean()
```

### Opponent join

Build team features first, then merge opponent’s pre-game features on `(game_id, opponent)` — never recompute opponent stats from a panel that still includes the current row’s outcome fields as if they were prior.

### Rest days

```python
g = panel.sort_values(["team", "gameday"]).groupby("team")
panel["rest_days"] = g["gameday"].diff().dt.days
# first game / offseason gaps need explicit handling (NA or capped)
```

Validate with EDA before trusting.

### Min history thresholds

```python
model_df = feat[
    (feat.pre_games_played >= 3) & (feat.opp_pre_games_played >= 3)
].copy()
```

Early season is noisy; do not pretend week-1 expanding means are stable.

---

## Anti-Patterns

| Anti-pattern | Fix |
|---|---|
| `rolling(5).mean()` without `shift(1)` | shift first |
| Final opponent season EPA on week 1 | expanding as-of only |
| Using `won` as a feature | target only |
| Mean-target encoding on full shuffle | fit inside train folds only |
| Same-game PBP as pre-game feature | redefine T or drop |
| Filling early-season NA with zeros silently | NA + threshold or league prior |

---

## Feature Card Template

Document each feature group:

```text
Feature group:
Decision time T:\nSources:
Transform:
Shift/as-of rule:
Legal at T: yes/no
Null policy / min history:
Used by models:
```

---

## Worked Example

```bash
python skills/feature-rules/scripts/feature_preview.py --seasons 2022-2024
python skills/feature-rules/scripts/legality_report.py --seasons 2023-2024 --out data/feature_legality.json
python skills/predictive-modeling/scripts/leakage_smoke.py
```

Expected:

- first team game has NA pre form
- `pre_win_pct` not identical to current `won`
- pipeline `FEATURE_COLS` contain no outcome fields

---

## Integrity Rules

1. Declare T before building features.
2. Illegal features are dropped, not “noted.”
3. Shift/as-of is mandatory for historical aggregates.
4. Min-history thresholds are part of the feature spec.
5. Run smoke/audit checks before claiming model metrics.

---

## Bundled Resources

### references/

| File | Contents |
|---|---|
| `legality_matrix.md` | legal/illegal/conditional matrix |
| `shift_patterns.md` | shift/roll/expand recipes |
| `feature_card_template.md` | documentation template |

### scripts/

| File | Contents |
|---|---|
| `feature_preview.py` | null rates + head of model features |
| `legality_report.py` | JSON legality check vs banned outcomes |

### package code

- `src/sports_ds/features/team_form.py`
- `src/sports_ds/pipelines/nfl_win_model.py` (`FEATURE_COLS`)

---

## Related Skills

| Need | Skill |
|---|---|
| EDA | `eda-sports` |
| Form/EWMA | `time-series-sports` |
| Ratings | `ratings-strength-models` |
| Leakage audit | `leakage-audit` |
| Baselines/models | `baseline-models`, `statistical-modeling`, `predictive-modeling` |

---

## Quick Command Card

```bash
python skills/feature-rules/scripts/feature_preview.py --seasons 2022-2024
python skills/feature-rules/scripts/legality_report.py --seasons 2023-2024
python skills/predictive-modeling/scripts/leakage_smoke.py
sports-ds nfl-win-pipeline --seasons 2018-2024
```
