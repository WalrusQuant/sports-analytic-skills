---
name: predictive-modeling
description: >
  Run sports predictive modeling with the sports_ds package. Use for NFL
  team-win modeling and walk-forward evaluation against baselines.
version: "0.2.0"
license: MIT
---

# Predictive Modeling

This skill operates the **real modeling code** in `src/sports_ds`.

## Do this

```bash
pip install -e .
sports-ds nfl-win-pipeline --seasons 2018-2024
```

## What the code does

- builds team-game panel from nflverse schedules
- engineers pre-game form features (`sports_ds.features.team_form`)
- walk-forward splits by season (`sports_ds.validation.splits`)
- fits:
  - constant win-rate baseline
  - logistic baseline
  - hist gradient boosting classifier
- prints log-loss / Brier / accuracy

## Code map

- pipeline: `src/sports_ds/pipelines/nfl_win_model.py`
- models: `src/sports_ds/models/`
- features: `src/sports_ds/features/team_form.py`
- CLI: `src/sports_ds/cli.py`

## Rules

1. Run baselines every time.
2. Do not hand-roll leaked rolling features; use package feature builders or mirror their shift(1) pattern.
3. Report walk-forward metrics, not one random split.
4. If extending to new targets (margin/total), add code under `models/` + `pipelines/`, not only markdown.

## Extend

```python
from sports_ds.pipelines.nfl_win_model import run_nfl_win_pipeline
result = run_nfl_win_pipeline(seasons=list(range(2018, 2025)))
```

## Output contract

- [ ] Command/pipeline ran
- [ ] Baseline + model metrics shown
- [ ] Seasons and row counts reported
- [ ] Notes if model fails to beat baseline
