---
name: ratings-strength-models
description: >
  Build and evaluate sports strength/rating models — Elo-like sequential
  ratings, offense/defense splits, least-squares power ratings, and as-of
  ratings for matchup prediction. Use for team/player strength baselines and
  as features in win/margin models. Includes a runnable Elo as-of builder.
version: "0.3.0"
license: MIT
metadata:
  version: "0.3.0"
---

# Ratings & Strength Models (Sports)

## Overview

Estimate latent team (or player) strength from past results, then use those
ratings only as they existed before game T. Ratings are often the strongest
simple sports baselines.

## When to Use This Skill

- Team power ratings / rankings over a season
- Matchup priors for win or margin models
- Opponent adjustment
- Strong baselines before feature-heavy ML

---

## Installation

```bash
pip install -e .
```

---

## Workflow

1. Choose the **result signal** (win, margin, goal diff, points ratio, EPA, runs).
2. Choose **update style** (sequential Elo-like vs batch season-to-date).
3. Fit/update using **only past games**.
4. Export an **as-of rating** for each team before each game.
5. Predict matchups from rating differentials (+ home).
6. Evaluate with season walk-forward (`validation-design`).
7. Compare to constant / home baselines (`baseline-models`).

---

## Model Families

| Family | Best for | Notes |
|---|---|---|
| Elo / Glicko-style | sequential win strength | easy as-of; margin optional |
| Offense/defense split | score models | attack vs defense ratings |
| Least-squares power ratings | season-to-date margins | solve system each week |
| Hierarchical strength | players with uneven n | partial pooling |
| Possession models | pace sports | sport-specific later |

Start with Elo-like or margin power ratings before exotic variants.

---

## Elo (implemented script)

Classic Elo update after each game, with home advantage and optional margin multiplier.

```bash
python skills/ratings-strength-models/scripts/elo_asof.py --seasons 2018-2024 --out data/elo_asof.csv
```

Outputs one row per team-game with `elo_pre`, `opp_elo_pre`, `elo_diff` known before the game.

Python pattern:

```python
import sys
from pathlib import Path
sys.path.append(str(Path("skills/ratings-strength-models/scripts").resolve()))
from elo_asof import build_elo_asof_table

from sports_ds.data.nfl import load_team_game_panel

panel = load_team_game_panel(list(range(2018, 2025)))
elo = build_elo_asof_table(panel, k=20.0, home_adv=65.0)
print(elo.head())
```

### Using Elo as a model feature

```python
import pandas as pd
from sports_ds.models.baselines import fit_logistic_baseline
from sports_ds.validation.splits import season_walk_forward_masks

df = elo.dropna(subset=["elo_diff"]).copy()
df["is_home"] = df["is_home"].astype(float)
for season, tr, te in season_walk_forward_masks(df):
    _, res, _ = fit_logistic_baseline(df, ["is_home", "elo_diff"], tr, te)
    print(season, res.log_loss, res.accuracy)
```

---

## Design Choices

### K factor

- Higher K: reacts faster, noisier
- Lower K: stabler, slower to adapt
- NFL starting point: K ≈ 20 on 1500-scale Elo

### Home advantage

- Add home_adv to home team pre-game Elo when computing expected score
- Estimate later from data; start with a fixed value

### Margin

- Optional multiplier on K using point differential
- Diminishing returns (log/sqrt) to avoid blowout domination

### Mean reversion / season regression

- Regress ratings to mean between seasons for multi-year series
- Important for long panels

---

## Evaluation

Primary:

- walk-forward log-loss / Brier for win probability from rating diff
- MAE for predicted margin if modeling spreads

Always compare to:

- constant baseline
- home-only model

---

## Hard Constraints

1. **As-of only** — never use post-game rating to predict that game.
2. Update order must follow real chronology.
3. Do not fit K on the final test season repeatedly without nested validation.
4. Report initialization and scale (e.g., mean 1500).

---

## Reporting Template

```text
Rating model: Elo
Signal: win (margin multiplier: …)
Params: K=…, home_adv=…, init=1500
As-of rule: pre-game rating before update
Validation: season walk-forward
Metrics vs constant / home: …
Limits: no roster continuity, no injuries, …
```

---

## Bundled Resources

### scripts/

- `elo_asof.py` — build pre-game Elo table from sports_ds NFL panel

### references/

- `rating_families.md`

### package handoff

- features: merge `elo_diff` into model frames
- validation: `sports_ds.validation.season_walk_forward_masks`
- baselines: `sports_ds.models.baselines`

---

## Related skills

- Baselines: `baseline-models`
- Features: `feature-rules`
- Predictive ML: `predictive-modeling`
- Validation: `validation-design`
