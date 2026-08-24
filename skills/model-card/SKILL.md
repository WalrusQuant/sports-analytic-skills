---
name: model-card
description: >
  Write a durable model card for a sports model: identity, intended use,
  target and decision time T, data, features, baselines, validation, results,
  limits, maintenance, and kill conditions. Use when documenting a kept model
  version for reuse or sharing — even if the user only says "document this
  model." Includes card templates, package-path examples for NFL/NBA/MLB, and a
  stub writer script.
version: "0.5.0"
license: MIT
metadata:
  version: "0.5.0"
---

# Model Card (Sports)

## Overview

Durable documentation for a sports analysis/prediction model.

A model card freezes what the model is for, how it was evaluated, what it must
not be used for, and when to kill or retrain it.

Use after a model is worth keeping. Pair with `experiment-log` for the trial
history that led here.

---

## When to Use This Skill

Use when:

- A model reaches a stable evaluation worth keeping
- Before sharing results beyond a scratch note
- Versioning a kept model
- User says “document this model” or “write a model card”

Do **not** use when:

- No model yet
- Quick scratch experiment with no keep decision → `experiment-log` only

---

## Installation

```bash
pip install -e .
# multi-sport models:
pip install -e ".[multi]"
```

---

## Required Inputs

- Model/process name and version
- Sport + target + prediction timestamp T (if predictive)
- Data window and sources
- Feature set (or `sports-ds feature-registry` names)
- Validation summary (walk-forward design + primary metric)
- Baseline comparison summary
- Leakage audit status
- Limits / failure modes
- Kill / retrain conditions

---

## Card Sections (required)

1. Identity
2. Intended use / not-for
3. Target and timing
4. Data
5. Features
6. Baselines
7. Validation
8. Results
9. Limits and failure modes
10. Maintenance / retrain / kill conditions
11. Linked experiments / package commands

Template: `references/card_template.md`  
Kill examples: `references/kill_conditions.md`

---

## Workflow

1. Gather evidence from modeling + validation + leakage work.
2. Draft all sections; use `unknown` explicitly when needed.
3. Remove unsupported claims.
4. Link `experiment-log` entries and exact CLI commands.
5. Freeze version (do not silently edit a frozen card — bump version).

```bash
python skills/model-card/scripts/write_card_stub.py --out data/model_card.md
python skills/model-card/scripts/write_card_stub.py --name nba_win_logit --version v1 --out data/nba_win_card.md
```

---

## Hard Constraints

1. Never omit baselines if performance is reported.
2. Never hide leakage/validation status.
3. Never present exploration as production-ready without saying so.
4. Kill conditions must be concrete and checkable.
5. Sport/grain/T must be explicit.

---

## Worked Examples

### NFL form win model

```text
Identity: nfl_home_win_logit_v3
Purpose: Estimate pre-kickoff P(team win) from home + form differentials
Data: nflverse schedules via sports_ds, 2018–2024
Validation: season walk-forward, primary metric log-loss
Result: logistic mean log-loss beat constant baseline on most folds
Leakage: CLEAN (sports-ds leakage-audit)
Kill conditions: two consecutive seasons failing baseline log-loss
Package paths:
  sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win.json
  sports-ds calibrate --sport nfl --seasons 2018-2024
  sports-ds leakage-audit --sport nfl --seasons 2023-2024
```

### NBA Elo baseline

```text
Identity: nba_elo_logit_v1
Purpose: P(team win) from as-of Elo differential + home
Data: sports_ds NBA panel (SDV schedules), 2023–2024
Validation: season walk-forward (min_train_seasons=1)
Package paths:
  sports-ds nba-elo --seasons 2023-2024 --min-train-seasons 1 --json-out data/nba_elo.json
  sports-ds leakage-audit --sport nba --seasons 2023-2024
```
\n### MLB margin model

```text
Identity: mlb_margin_ridge_v1
Purpose: Predict pre-game run differential
Data: sports_ds MLB panel, 2023–2024
Validation: season walk-forward; primary metric MAE vs constant mean
Package paths:
  sports-ds mlb-margin-pipeline --seasons 2023-2024 --min-train-seasons 1
```

---

## Bundled Resources

### references/
- `card_template.md`
- `kill_conditions.md`

### scripts/
- `write_card_stub.py`

---

## Related Skills

- `experiment-log`
- `results-reporting`
- `validation-design`
- `baseline-models`
- `sports-modeling-doctrine`
- `leakage-audit`

---

## Quick Command Card

```bash
python skills/model-card/scripts/write_card_stub.py --out data/model_card.md
sports-ds feature-registry | head
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win_pipeline.json
sports-ds nba-elo --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-margin-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds leakage-audit --sport nba --seasons 2023-2024
sports-ds calibrate --sport mlb --seasons 2023-2024 --min-train-seasons 1
```
