---
name: sports-modeling-doctrine
description: >
  Core doctrine for sports data science: define the analysis/prediction
  question, baselines, time-safe evaluation, metrics, and when a sports model
  is good enough. Use at the start of modeling or analysis work before choosing
  algorithms. Sports-specific standards for agents building predictive or
  explanatory models on games, teams, and players.
version: "0.3.0"
license: MIT
metadata:
  version: "0.3.0"
---

# Sports Modeling Doctrine

## Overview

Before code, lock the scientific contract of the sports analysis:

- what question is being answered
- what is known at time T
- what baseline counts as “something”
- how success is measured out of time

This skill is the front door for sports modeling work.

## When to Use This Skill

- Starting any sports modeling or analysis project
- Choosing what “good” means
- Preventing notebook chaos before feature soup
- Reviewing whether a claimed model result is even evaluable

---

## Workflow

1. **Write the question in one sentence.**
2. **Name the grain** (game, team-game, player-game, possession, pitch).
3. **If predictive: write decision time T.**
4. **Name the target** and base rate.
5. **Name baselines** before candidate models.
6. **Name primary metric** before fitting.
7. **Name validation design** (default: season walk-forward).
8. **Only then** load data and model (`eda-sports` → `feature-rules` → models).

---

## Question Types

| Type | Example | Success looks like |
|---|---|---|
| Predict | P(home win), expected margin | beat baselines walk-forward |
| Explain | home advantage size after controls | stable effect + uncertainty |
| Rank | team strength through week W | correlates with future results |
| Simulate | season win distribution | calibrated inputs + uncertainty |

Do not mix “explain coefficients” claims with “predictive superiority” claims without running both evaluations.

---

## Non-Negotiables

1. **Time order matters.** Random game shuffles are usually invalid for season sports.
2. **Baselines first.** Constant / home / simple rating beat claims of ML value.
3. **Features must be legal at T** for predictive work.
4. **Primary metric locked before peeking at test folds.**
5. **Report failures.** Non-improvement is a valid result.
6. **Public sports data first** (nflverse, SportsDataverse, pybaseball, etc.).

---

## Default Metric Guide

| Target | Primary metric |
|---|---|
| Win probability | log-loss (Brier secondary) |
| Margin | MAE |
| Counts (goals/runs) | MAE / Poisson deviance |
| Ranking | future-result correlation on holdout |

Accuracy alone is not enough.

---

## Project Charter Template

```text
Question: …
Sport/league: …
Grain: …
Predictive?: yes/no
Decision time T: …
Target: …
Base rate / null: …
Baselines: …
Primary metric: …
Validation: season walk-forward (min_train_seasons=…)
Data sources: …
Out of scope: …
```

Save this in the experiment log before fitting.

---

## Agent Operating Rules

When acting as an agent on this repo:

1. Read this doctrine before inventing a custom pipeline.
2. Prefer `sports_ds` package entrypoints and skill scripts over ad-hoc scrapers.
3. Run EDA before modeling.
4. Run leakage checks when metrics look strong.
5. Hand off to specialized skills rather than one mega-prompt.

---

## Worked Default (NFL team wins)

```text
Question: Predict pre-game P(team win) on NFL team-game panel.
Grain: team-game
T: scheduled kickoff
Target: won
Baselines: constant train rate; logistic on home + form diffs
Primary metric: log-loss
Validation: season walk-forward
Implementation: sports-ds nfl-win-pipeline
```

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024
```

---

## Bundled Resources

### references/

- `charter_examples.md`

### scripts/

- `print_charter_template.py` — emit a blank charter file

---

## Related skills

- EDA: `eda-sports`
- Features: `feature-rules`
- Baselines: `baseline-models`
- Stats: `statistical-modeling`
- ML: `predictive-modeling`
- Ratings: `ratings-strength-models`
- Validation: `validation-design`
- Leakage: `leakage-audit`
