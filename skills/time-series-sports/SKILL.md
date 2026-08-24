---
name: time-series-sports
description: >
  Time-series and form modeling for sports: rolling performance, expanding
  windows, EWMA/recency weighting, rest adjustments, regime shifts, early-season
  shrinkage, and forecasting team or player form before game T. Use when history
  order and recent form matter — even if the user only says "hot streak,"
  "rolling average," or "recent form." Includes sports_ds form builders, feature
  registry, EWMA scripts, multi-sport panel paths, and strict shift-before-aggregate
  rules.
version: "0.6.0"
license: MIT
metadata:
  version: "0.6.0"
---

# Time Series & Form (Sports)

## Overview

Sports performance is ordered in time. This skill builds **form features** and
simple trajectory forecasts that are legal at decision time T:\n\n- rolling means\n- expanding rates\n- EWMA / decay\n- rest gaps\n- regime flags\n\nPackage implementation used by the win/margin pipelines:

`sports_ds.features.team_form.add_pregame_form_features`

Feature legality registry:

`sports-ds feature-registry`

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
pip install -e .
# multi-sport panels:
pip install -e ".[multi]"
```

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

Recipes: `references/form_feature_recipes.md`  
Shrinkage: `references/early_season.md`  
Rest: `references/rest_and_gaps.md`

---

## Package Form Features

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.data.nba import load_nba_team_game_panel
from sports_ds.data.mlb import load_mlb_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.features.registry import list_feature_specs

panel = load_team_game_panel([2022, 2023, 2024])
feat = add_pregame_form_features(panel, windows=[3, 5])
print(list_feature_specs()[:3])
```

Creates shifted fields such as:

- `pre_win_pct`, `pre_avg_diff`, `pre_games_played`
- `roll3_win_pct`, `roll5_diff`
- opponent mirrors and differentials used by the win model

Code: `src/sports_ds/features/team_form.py`  
Registry: `src/sports_ds/features/registry.py`

```bash
sports-ds feature-registry
```

---

## Scripts

### Form preview (package features)

```bash
python skills/feature-rules/scripts/feature_preview.py --seasons 2023-2024
```

### EWMA form table

```bash
python skills/time-series-sports/scripts/ewma_form.py \
  --seasons 2023-2024 \
  --span 5 \
  --out data/ewma_form.csv
```

Builds team-game EWMA of prior wins and point differential (shifted), plus opponent differentials.

### Compare rolling vs EWMA quickly

```bash
python skills/time-series-sports/scripts/compare_form_windows.py --seasons 2018-2024
```

---

## Multi-sport form path

Form features are sport-agnostic on the shared panel contract:

```bash
# NFL
sports-ds nfl-win-pipeline --seasons 2018-2024
# NBA / MLB
sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-margin-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds leakage-audit --sport nba --seasons 2023-2024
```

Same shift rules apply on every sport panel.

---

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

Form features are hypotheses. Evaluate them:

```bash
python skills/baseline-models/scripts/run_baselines.py --seasons 2018-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
```

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
python skills/feature-rules/scripts/feature_preview.py --seasons 2023-2024
python skills/time-series-sports/scripts/ewma_form.py --seasons 2023-2024 --span 5
python skills/time-series-sports/scripts/compare_form_windows.py --seasons 2018-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
sports-ds leakage-audit --sport nfl --seasons 2023-2024
```

---

## Bundled Resources

### references/
| File | Contents |
|---|---|
| `form_feature_recipes.md` | shift/roll/expand/EWMA recipes |
| `early_season.md` | small-sample handling |
| `rest_and_gaps.md` | byes and calendar gaps |

### scripts/
| File | Contents |
|---|---|
| `ewma_form.py` | shifted EWMA form table |
| `compare_form_windows.py` | walk-forward compare roll vs EWMA features |

### package code
- `src/sports_ds/features/team_form.py`
- `src/sports_ds/features/registry.py`

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
sports-ds feature-registry | head
python skills/feature-rules/scripts/feature_preview.py --seasons 2023-2024
python skills/time-series-sports/scripts/ewma_form.py --seasons 2023-2024 --span 5
python skills/time-series-sports/scripts/compare_form_windows.py --seasons 2018-2024
python skills/baseline-models/scripts/run_baselines.py --seasons 2018-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
```
