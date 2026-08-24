---
name: sports-modeling-doctrine
description: >
  Core doctrine for sports data science: define the analysis or prediction
  question, grain, decision time T, baselines, primary metrics, time-safe
  evaluation, and when a sports model is good enough. Use at the start of
  modeling or analysis work before choosing algorithms — even if the user only
  says "help me model this" or "where do I start." Includes charter templates,
  multi-sport package path map, and agent operating rules for the whole skill
  pack.
version: "0.6.0"
license: MIT
metadata:
  version: "0.6.0"
---

# Sports Modeling Doctrine

## Overview

Before code, lock the scientific contract of the sports analysis:

- what question is being answered
- what is known at time T
- what baseline counts as “something”
- how success is measured out of time

This skill is the **front door** for sports modeling work in this pack.

If the charter fields are not named, do not fit models.

---

## When to Use This Skill

Use when:

- Starting any sports modeling or analysis project
- Choosing what “good” means
- Preventing notebook chaos before feature soup
- Reviewing whether a claimed model result is even evaluable
- User says “where do I start?” or “help me model this”
- Choosing among NFL/NBA/MLB package paths

Do **not** skip this and jump to algorithms.

| Need | Go instead after charter |
|---|---|
| Load data | `nflreadpy` / `sportsdataverse-py` / `pybaseball` |
| EDA | `eda-sports` |
| Features | `feature-rules` |
| Baselines | `baseline-models` |
| ML | `predictive-modeling` |
| Stats | `statistical-modeling` |

---

## Installation

No special deps beyond the pack. For runnable pipelines:

```bash
pip install -e .
# multi-sport:
pip install -e ".[multi]"
```

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
9. **Write the charter** (template below).
10. **Log the experiment** before claiming keep/discard.

---

## Question Types

| Type | Example | Success looks like |
|---|---|---|
| Predict | P(home win), expected margin | beat baselines walk-forward |
| Explain | home advantage size after controls | stable effect + uncertainty |
| Rank | team strength through week W | correlates with future results |
| Simulate | season win distribution | calibrated inputs + uncertainty |

Do not mix “explain coefficients” claims with “predictive superiority” claims without running both evaluations.

Examples: `references/charter_examples.md`

---

## Non-Negotiables

1. **Time order matters.** Random game shuffles are usually invalid for season sports.
2. **Baselines first.** Constant / home / simple rating beat claims of ML value.
3. **Features must be legal at T** for predictive work.
4. **Primary metric locked before peeking at test folds.**
5. **Report failures.** Non-improvement is a valid result.
6. **Public sports data first** (nflverse, SportsDataverse, pybaseball, etc.).
7. **Leakage audit before shipping strong claims.**

---

## Default Metric Guide

| Target | Primary metric |
|---|---|
| Win probability | log-loss (Brier secondary) |
| Margin | MAE |
| Counts | MAE / Poisson deviance |
| Ranking | future-result correlation on holdout |

Accuracy alone is not enough.  
See `references/good_enough.md`.

---

## Project Charter Template

```text
Question:
Sport/league:
Grain:
Predictive?: yes/no
Decision time T:\nTarget:
Base rate / null:
Baselines:
Primary metric:
Validation: season walk-forward (min_train_seasons=…)
Data sources:
Package path:
Out of scope:
```

```bash
python skills/sports-modeling-doctrine/scripts/print_charter_template.py
python skills/sports-modeling-doctrine/scripts/print_charter_template.py --out data/charter.md
```

Save the charter in the experiment log before fitting.

---

## Package Path Map (after charter)

| Sport / target | Default package path |
|---|---|
| NFL win | `sports-ds nfl-win-pipeline` |
| NFL margin | `sports-ds nfl-margin-pipeline` |
| NFL Elo baseline | `sports-ds nfl-elo` |
| NBA win | `sports-ds nba-win-pipeline` |
| NBA margin | `sports-ds nba-margin-pipeline` |
| NBA Elo | `sports-ds nba-elo` |
| MLB win | `sports-ds mlb-win-pipeline` |
| MLB margin | `sports-ds mlb-margin-pipeline` |
| MLB Elo | `sports-ds mlb-elo` |
| Trust checks | `sports-ds leakage-audit --sport …`, `sports-ds calibrate --sport …` |

Pipeline map detail: `references/skill_path.md`

---

## Agent Operating Rules

When acting as an agent on this repo:

1. Read this doctrine before inventing a custom pipeline.
2. Prefer `sports_ds` package entrypoints and skill scripts over ad-hoc scrapers.
3. Run EDA before modeling.
4. Run leakage checks when metrics look strong.
5. Hand off to specialized skills rather than one mega-prompt.
6. Keep the simplest model that wins.
7. Do not leave thin skill stubs when the user asked for full depth.

---

## Worked Defaults

### NFL team wins
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

### NBA Elo baseline
```bash
sports-ds nba-elo --seasons 2023-2024 --min-train-seasons 1
```

### MLB margin
```bash
sports-ds mlb-margin-pipeline --seasons 2023-2024 --min-train-seasons 1
```

---

## Integrity Rules

1. No algorithm before charter fields are named.
2. No “good model” claim without baseline + walk-forward.
3. No silent scope expansion mid-project.
4. Non-results get written down.
5. Multi-sport claims require the matching package command, not NFL copy-paste.

---

## Output Contract

Done means:

- [ ] Question written
- [ ] Grain + T (if predictive) written
- [ ] Baselines + primary metric locked
- [ ] Validation design named
- [ ] Package path named
- [ ] Charter saved

---

## Bundled Resources

### references/
| File | Contents |
|---|---|
| `charter_examples.md` | example charters |
| `good_enough.md` | success/failure rules |
| `skill_path.md` | default skill sequence |

### scripts/
| File | Contents |
|---|---|
| `print_charter_template.py` | emit blank charter |

---

## Related Skills

| Next | Skill |
|---|---|
| EDA | `eda-sports` |
| Features | `feature-rules` |
| Baselines | `baseline-models` |
| Stats | `statistical-modeling` |
| ML | `predictive-modeling` |
| Ratings | `ratings-strength-models` |
| Validation | `validation-design` |
| Leakage | `leakage-audit` |

---

## Quick Command Card

```bash
python skills/sports-modeling-doctrine/scripts/print_charter_template.py --out data/charter.md
sports-ds nfl-eda --seasons 2024
sports-ds nfl-win-pipeline --seasons 2018-2024
sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-elo --seasons 2023-2024 --min-train-seasons 1
```
