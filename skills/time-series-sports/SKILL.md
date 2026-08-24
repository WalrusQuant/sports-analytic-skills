---
name: time-series-sports
description: >
  Time-series and form modeling for sports: rolling performance, expanding
  windows, EWMA/recency weighting, rest adjustments, regime shifts, and
  forecasting team or player form before game T. Use when history order and
  recent form matter. Includes scripts for form feature tables and EWMA previews.
version: "0.3.0"
license: MIT
metadata:
  version: "0.3.0"
---

# Time Series & Form (Sports)

## Overview

Sports performance is ordered in time. This skill builds **form features** and
simple trajectory forecasts that are legal at decision time T: rolling means,
expanding rates, EWMA/decay, rest gaps, and regime flags.

Package implementation already used by the win pipeline:

`sports_ds.features.team_form.add_pregame_form_features`

## When to Use This Skill

- Team/player form features for pre-game models
- Rolling averages, EWMA, half-life decay
- Forecasting next-game stats from trajectories
- Handling bye weeks, missing games, season breaks
- Comparing recency-weighted form vs static season averages

## When Not to Use

- Pure cross-sectional comparison with no recency component
- Static season aggregates already sufficient and time-safe

---

## Installation

```bash
pip install -e .
```

---

## Workflow

1. Define the **entity** and **frequency** (team-game, player-game, week).
2. Sort by entity + time; handle missing games explicitly.
3. Choose window/decay rules; tune only inside training folds.
4. Apply **shift(1)** / as-of so current game is never inside the feature.
5. Compare form features against static baselines under walk-forward validation.
6. Watch early-season small-sample explosions — use min-games thresholds or shrinkage.

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

---

## Package Form Features

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features

panel = load_team_game_panel([2022, 2023, 2024])
feat = add_pregame_form_features(panel, windows=(3, 5))
```

Creates shifted fields such as:

- `pre_win_pct`, `pre_avg_diff`, `pre_games_played`
- `roll3_win_pct`, `roll5_diff`
- opponent mirrors and differentials used by the win model

---

## Scripts

### Form preview (package features)

```bash
python skills/feature-rules/scripts/feature_preview.py --seasons 2023-2024
```

### EWMA form table

```bash
python skills/time-series-sports/scripts/ewma_form.py --seasons 2023-2024 --span 5 --out data/ewma_form.csv
```

Builds team-game EWMA of prior point differential and wins (shifted).

---

## Early-Season Handling

| Problem | Mitigation |
|---|---|
| Week 1 empty history | NA features + drop or league prior |
| Tiny n rolling windows | require `pre_games_played >= k` |
| Noisy short rolls | shrinkage toward league mean / expanding mean |
| Bye weeks | rest_days feature; don't fill with zeros blindly |

---

## Hard Constraints

1. No centered rolling windows that peek forward.
2. No “season average including current game.”
3. Early-season priors/shrinkage when n is tiny.
4. Validate across seasons, not one hot streak.
5. Opponent strength still matters — raw form is not opponent-adjusted strength (`ratings-strength-models`).

---

## Anti-Patterns

- Fixed 5-game mean with no shrinkage
- Ignoring opponent strength in raw form
- Treating playoffs and regular season as identical without a flag
- Tuning window length on the final test season only

---

## Reporting Template

```text
Form model: rolling / EWMA / expanding
Entity/frequency: …
Windows/span: …
Shift rule: shift(1) before aggregate
Min history: …
Validation: vs static baseline under walk-forward
Limits: early season, injuries, opponent strength…
```

---

## Bundled Resources

### scripts/

- `ewma_form.py` — shifted EWMA win% and point-diff form table

### references/

- `form_feature_recipes.md`

### package code

- `src/sports_ds/features/team_form.py`

---

## Related Skills

- Feature legality: `feature-rules`
- Ratings (opponent-adjusted): `ratings-strength-models`
- EDA: `eda-sports`
- Models: `baseline-models`, `predictive-modeling`
