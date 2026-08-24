---
name: feature-rules
description: >
  Build time-safe sports features for pre-game modeling — as-of joins, shifted
  rolling form, opponent differentials, and legality labels. Use when creating
  feature matrices for wins/margins/player stats or reviewing whether features
  could know the future. Includes sports_ds.team_form builders.
version: "0.3.0"
license: MIT
metadata:
  version: "0.3.0"
---

# Feature Rules for Sports

## Overview

A feature is legal for prediction at time T only if it would have been knowable
at T. This skill defines the rules and the `sports_ds` builders that implement them.

## When to Use

- Building pre-game team/player features
- Reviewing a feature matrix for look-ahead
- Extending form windows, rest features, rating differentials

---

## Installation

```bash
pip install -e .
```

---

## Legality Test

For every feature:

> At prediction time T, could an analyst know this value from published info at or before T?

| Answer | Action |
|---|---|
| Yes | legal |
| Only with delay | shift by delay |
| No | illegal for this T |
| Partially | encode known portion only |

---

## Implemented Builder: pre-game team form

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features

panel = load_team_game_panel([2022, 2023, 2024])
feat = add_pregame_form_features(panel, windows=[3, 5])
```

Creates shifted features:

- `pre_win_pct`, `pre_avg_pf`, `pre_avg_pa`, `pre_avg_diff`, `pre_games_played`
- `rollW_win_pct`, `rollW_diff`
- opponent mirrors (`opp_*`)
- differentials used by the win model:
  - `feature_win_pct_diff`
  - `feature_diff_diff`
  - `feature_roll3_win_diff`
  - `feature_roll5_diff_diff`

All group operations use `shift(1)` before expanding/rolling.

Code: `src/sports_ds/features/team_form.py`

---

## Feature Families

### Usually legal if as-of T

- prior-game aggregates ending before T
- schedule context (home/away, rest days from known schedule)
- ratings computed only from past games

### Illegal for pre-game T

- current game points/yards/EPA
- final season averages applied to early weeks
- post-game player participation used as pre-game availability without timestamp

### Conditional

- injury reports (only with timestamped source)
- in-game live features (only if T is in-game)

---

## Rest Days Example (pattern)

```python
# conceptual pattern: sort team games, compute days since previous game, shift-safe
g = panel.sort_values(["team", "gameday"]).groupby("team")
panel["rest_days"] = g["gameday"].diff().dt.days
# rest_days already refers to gap before current game when computed as diff on sorted games
```

Validate with EDA before trusting.

---

## Procedure

1. Declare T.
2. List raw fields + known-times.
3. Build features with shift/as-of only.
4. Label each feature legal/illegal.
5. Drop illegal features.
6. Set min history thresholds (`pre_games_played >= n`).
7. Pass to baselines/models under walk-forward validation.
8. Run leakage smoke tests.

```bash
python skills/predictive-modeling/scripts/leakage_smoke.py
python skills/feature-rules/scripts/feature_preview.py --seasons 2023-2024
```

---

## Anti-Patterns

- `rolling(5).mean()` without `shift(1)`
- merging final opponent season stats onto week 1
- using `won` as a feature
- mean-target encoding fit on full shuffled dataset

---

## Bundled Resources

### references/

- `legality_matrix.md`

### scripts/

- `feature_preview.py` — show feature null rates and head

### package code

- `src/sports_ds/features/team_form.py`

---

## Handoffs

- EDA → `eda-sports`
- Leakage audit → `leakage-audit`
- Models → `baseline-models` / `statistical-modeling` / `predictive-modeling`

---

## Command Card

```bash
python skills/feature-rules/scripts/feature_preview.py --seasons 2022-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
```
