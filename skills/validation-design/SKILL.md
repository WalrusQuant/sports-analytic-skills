---
name: validation-design
description: >
  Design and run time-safe validation for sports models — season walk-forward,
  expanding vs sliding windows, embargo rules, metric locks, nested tuning,
  fold reporting, and validation charters. Use before claiming a model works,
  when replacing random K-fold on games/seasons, reviewing a backtest, or
  wiring sports_ds.validation into a new pipeline. Covers probability and
  regression metrics and common sports split failure modes.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# Validation Design for Sports

## Overview

Sports results are ordered in time. Random row splits leak future structure
(roster state, scheme, strength of schedule paths).

This skill standardizes **time-safe validation** and hooks it to `sports_ds`:

- lock metrics before fitting
- walk forward by season (default)
- tune only inside training data
- report per-fold and mean metrics vs baselines
- write a validation charter an agent can follow

---

## When to Use This Skill

Use when:

- Any predictive sports model evaluation
- Designing folds for a new pipeline
- Reviewing someone else’s backtest design
- Choosing metrics before fitting
- User says “is this validation legit?” or “use cross-validation”

Do **not** use when:

- Pure EDA with no model → `eda-sports`
- One-off coefficient exploration on a fixed window (say explicitly it is **not** walk-forward)
- Leakage is about features, not splits → still pair with `leakage-audit`

---

## Installation

```bash
pip install -e .
```

---

## Default Protocol

1. Sort entities by time (`season`, `week`, `gameday`).
2. Choose **primary metric before fitting** (log-loss for probs; MAE for margins).
3. Walk forward by season (or another honest time block).
4. Train only on past blocks.
5. Tune only inside training data (nested or fixed a priori).
6. Report per-fold and mean metrics **vs baselines**.
7. Do not revisit the final fold repeatedly to shop results.
8. Write the charter (template below).

Skipping baselines or using random K-fold on seasons is a failed design.

---

## Implemented Splitter

```python
from sports_ds.validation.splits import season_walk_forward_masks

for test_season, train_mask, test_mask in season_walk_forward_masks(df, min_train_seasons=2):
    train = df.loc[train_mask]
    test = df.loc[test_mask]
    ...
```

Behavior:

- seasons sorted ascending
- for test season `S`, train = all seasons `< S`
- skips until `min_train_seasons` prior seasons exist

Code: `src/sports_ds/validation/splits.py`

### Inspect fold sizes

```bash
python skills/validation-design/scripts/print_folds.py --seasons 2018-2024
python skills/validation-design/scripts/print_folds.py --seasons 2018-2024 --min-train-seasons 3
```

---

## Full Evaluation Example

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.models.baselines import baseline_home_rate, fit_logistic_baseline
from sports_ds.validation.splits import season_walk_forward_masks

panel = load_team_game_panel(list(range(2018, 2025)))
df = add_pregame_form_features(panel)
features = ["is_home", "feature_win_pct_diff", "feature_diff_diff"]
df = df.dropna(subset=features + ["won"])

for season, tr, te in season_walk_forward_masks(df, min_train_seasons=2):
    b = baseline_home_rate(df, tr, te)
    _, m, _ = fit_logistic_baseline(df, features, tr, te)
    print(season, b.log_loss, m.log_loss, m.accuracy)
```

Or the full pipeline:

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024
```

---

## Metric Lock Guide

Lock **one primary metric** before candidates.

| Task | Primary | Secondary |
|---|---|---|
| Win probability | log-loss | Brier, calibration (ECE) |
| Margin | MAE | RMSE, bias |
| Counts | MAE / Poisson deviance | rate calibration |
| Ranking | Spearman on holdout period | pairwise accuracy |

Accuracy alone is not enough.  
Details: `references/metrics_lock.md`, `predictive-modeling` metrics refs.

---

## Design Patterns

### Season walk-forward (default)

Best default for NFL / NBA / MLB / NHL season sports.

```text
train < 2020 → test 2020
train < 2021 → test 2021
...
```

### Expanding vs sliding train window

| Style | Train set | When |
|---|---|---|
| Expanding | all past seasons | default; more data |
| Sliding | last K seasons only | major rule/style regime break |

### Week walk-forward (in-season)

Useful for large within-season samples. Still never train on week t labels to predict week t without shift-safe features.

### Embargo

If official stats settle days after a game, leave a gap between train max date and test min date.

### Grouping / panel caution

Team-game panels have **two rows per game**. Interpreting accuracy as “game pick accuracy” requires care (double counting). Prefer log-loss on team rows or evaluate on home rows only for game-level claims.

### Nested tuning

```text
Outer fold: test season S
Inner: walk-forward or hold out latest train season for hyperparams
Final: refit chosen config on all train seasons < S, score S once
```

Never search hyperparameters on S.

---

## Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| Random K-fold on games | future leaks into train |
| StandardScaler fit on full dataset before split | test statistics leak |
| Early stopping on true test fold | test becomes tune set |
| Dropping the ugly season after seeing scores | selection bias |
| Tuning until one holdout looks good | overfitting the protocol |
| Reporting only mean, hiding bad folds | dishonest |
| No baseline | uninterpretable “good” numbers |

See `references/split_patterns.md` and `references/anti_patterns.md`.

---

## Validation Charter Template

Write this **before** fitting candidates:

```text
Validation charter
Target:
Grain:
Decision time T:\nPrimary metric:
Secondary metrics:
Baselines:
Split: season walk-forward
min_train_seasons:
Window: expanding | sliding(K=)
Tune: inside training only (describe)
Success rule: beat baselines on mean primary metric AND on ≥ majority of folds
Leakage checks required: yes (feature-rules / leakage-audit)
Reporting: per-fold table + mean + decision
```

Script:

```bash
python skills/validation-design/scripts/write_charter.py --out data/validation_charter.md
```

---

## Reporting Requirements

A validation writeup is incomplete without:

1. charter (or equivalent fields)
2. baseline metrics
3. candidate metrics
4. **per-fold table**
5. mean summary
6. success rule pass/fail
7. limits (panel grain, incomplete seasons, etc.)

---

## Worked Example (NFL wins)

```bash
python skills/validation-design/scripts/print_folds.py --seasons 2018-2024
python skills/baseline-models/scripts/run_baselines.py --seasons 2018-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
```

Charter sketch:

```text
Target: won
Grain: team-game
T: kickoff
Primary metric: log-loss
Baselines: constant train rate; logistic form features
Split: season walk-forward, min_train_seasons=2
Success: mean log-loss < constant and better on most seasons
```

---

## Integrity Rules

1. Lock metrics before peeking at test folds.
2. Train time strictly before test time.
3. Always include baselines.
4. Publish ugly folds.
5. Nested or a-priori tuning only.
6. Do not redefine success after seeing results.

---

## Bundled Resources

### references/

| File | Contents |
|---|---|
| `split_patterns.md` | walk-forward patterns |
| `metrics_lock.md` | primary metric choices |
| `anti_patterns.md` | validation failures |

### scripts/

| File | Contents |
|---|---|
| `print_folds.py` | fold sizes for a season range |
| `write_charter.py` | blank validation charter file |

### package code

- `src/sports_ds/validation/splits.py`
- `src/sports_ds/pipelines/nfl_win_model.py`

---

## Related Skills

| Need | Skill |
|---|---|
| Features | `feature-rules` |
| Baselines | `baseline-models` |
| Models | `statistical-modeling`, `predictive-modeling` |
| Leakage | `leakage-audit` |
| Calibration | `calibration-check` |
| Report | `results-reporting`, `experiment-log` |

---

## Quick Command Card

```bash
python skills/validation-design/scripts/print_folds.py --seasons 2018-2024
python skills/validation-design/scripts/write_charter.py --out data/validation_charter.md
sports-ds nfl-win-pipeline --seasons 2018-2024
```
