---
name: model-card
description: >
  Write a durable model card for a sports model: identity, intended use,
  target and decision time T, data, features, baselines, validation, results,
  limits, maintenance, and kill conditions. Use when documenting a kept model
  version for reuse or sharing — even if the user only says "document this
  model." Includes card templates and a stub writer script.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# Model Card (Sports)

## Overview

Durable documentation for a sports analysis/prediction model.

A model card freezes what the model is for, how it was evaluated, what it must
not be used for, and when to kill or retrain it.

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

No special deps. Optional:

```bash
pip install -e .
```

---

## Required Inputs

- Model/process name and version
- Target and prediction timestamp T (if predictive)
- Data window and sources
- Validation summary
- Baseline comparison summary
- Leakage audit status
- Limits / failure modes

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
11. Linked experiments

Template: `references/card_template.md`

---

## Workflow

1. Gather evidence from modeling + validation + leakage work.
2. Draft all sections; use `unknown` explicitly when needed.
3. Remove unsupported claims.
4. Link `experiment-log` entries.
5. Freeze version (do not silently edit a frozen card — bump version).

```bash
python skills/model-card/scripts/write_card_stub.py --out data/model_card.md
```

---

## Hard Constraints

1. Never omit baselines if performance is reported.
2. Never hide leakage/validation status.
3. Never present exploration as production-ready without saying so.
4. Kill conditions must be concrete and checkable.

---

## Worked Example

```text
Identity: home_win_logit_v3
Purpose: Estimate pre-kickoff P(team win) from home + form differentials
Data: nflverse schedules via sports_ds, 2018–2024
Validation: season walk-forward, primary metric log-loss
Result: logistic mean log-loss beat constant baseline on most folds
Leakage: CLEAN (sports-ds leakage-audit / package audit_pregame_form_features)
Kill conditions: two consecutive seasons failing baseline log-loss; major rule/regime break without revalidation
Package paths:
  sports-ds nfl-win-pipeline --seasons 2018-2024
  sports-ds calibrate --seasons 2018-2024
  sports-ds leakage-audit --seasons 2023-2024
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
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win_pipeline.json
sports-ds leakage-audit --seasons 2023-2024
sports-ds calibrate --seasons 2018-2024
```
