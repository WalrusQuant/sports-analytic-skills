---
name: validation-design
description: >
  Design and run time-safe validation for sports models — season walk-forward,
  embargo rules, metric locks, and fold reporting. Use before claiming a model
  works, when replacing random K-fold on games/seasons, or when wiring
  sports_ds.validation into a new pipeline.
version: "0.3.0"
license: MIT
metadata:
  version: "0.3.0"
---

# Validation Design for Sports

## Overview

Sports results are ordered in time. Random row splits leak future structure.
This skill standardizes walk-forward validation and hooks it to `sports_ds`.

## When to Use

- Any predictive sports model evaluation
- Designing folds for a new pipeline
- Reviewing someone else’s backtest design
- Choosing metrics before fitting

## When Not to Use

- Pure EDA with no model
- One-off coefficient exploration on a fixed window (still say it is not walk-forward)

---

## Installation

```bash
pip install -e .
```

---

## Default Protocol

1. Sort entities by time (`season`, `week`, `gameday`).
2. Choose primary metric **before** fitting (log-loss for probs; MAE for margins).
3. Walk forward by season (or another honest time block).
4. Train only on past blocks.
5. Tune only inside training data.
6. Report per-fold and mean metrics vs baselines.
7. Do not revisit the final fold repeatedly to shop results.

---

## Implemented Splitter

```python
from sports_ds.validation.splits import season_walk_forward_masks

for test_season, train_mask, test_mask in season_walk_forward_masks(df, min_train_seasons=2):
    ...
```

Behavior:

- seasons sorted ascending
- for test season S, train = all seasons < S
- skips until `min_train_seasons` prior seasons exist

---

## Full Evaluation Example

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.models.baselines import baseline_home_rate, fit_logistic_baseline
from sports_ds.validation.splits import season_walk_forward_masks

panel = load_team_game_panel(list(range(2018, 2025)))
df = add_pregame_form_features(panel).dropna()
features = ["is_home", "feature_win_pct_diff", "feature_diff_diff"]

for season, tr, te in season_walk_forward_masks(df):
    b = baseline_home_rate(df, tr, te)
    _, m, _ = fit_logistic_baseline(df, features, tr, te)
    print(season, b.log_loss, m.log_loss)
```

Or:

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024
```

---

## Metric Lock Guide

| Task | Primary | Secondary |
|---|---|---|
| Win probability | log-loss | Brier, calibration |
| Margin | MAE | RMSE, bias |
| Counts | MAE / deviance | calibration of rates |
| Ranking | Spearman on holdout period | pairwise accuracy |

Accuracy alone is not enough for imbalanced or base-rate-driven outcomes.

---

## Design Patterns

### Season walk-forward (default)

Best default for NFL/NBA/MLB season sports.

### Expanding vs sliding train window

- Expanding: all past seasons (more data)
- Sliding: last K seasons only (if rules/style changed)

### Grouping

Never split rows from the same game across train/test for game-level leakage edge cases. Team-game panels used here evaluate each team row; be careful interpreting accuracy as game accuracy (double rows per game).

### Embargo

If features settle days after a game (official corrections), leave a gap between train max date and test min date.

---

## Anti-Patterns

- Random K-fold on games
- StandardScaler fit on full dataset before split
- Early stopping against the true test fold
- Dropping the ugly season after seeing scores
- Tuning until one holdout looks good

---

## Validation Charter Template

```text
Target: …
Grain: …
Decision time T: …
Primary metric: …
Baselines: …
Split: season walk-forward, min_train_seasons=2
Tune: inside training seasons only
Success: beat baselines on mean walk-forward primary metric and on ≥ majority of folds
```

---

## Bundled Resources

### references/

- `split_patterns.md`

### scripts/

- `print_folds.py` — show walk-forward fold sizes for a season range

### package code

- `src/sports_ds/validation/splits.py`
- `src/sports_ds/pipelines/nfl_win_model.py`

---

## Handoffs

- Features → `feature-rules`
- Models → `statistical-modeling` / `predictive-modeling`
- Leakage → `leakage-audit`
- Report → `results-reporting`

---

## Command Card

```bash
python skills/validation-design/scripts/print_folds.py --seasons 2018-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
```
