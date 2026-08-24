---
name: ratings-strength-models
description: >
  Build and evaluate sports strength/rating models — Elo-like sequential
  ratings, offense/defense splits, least-squares power ratings, hierarchical
  strength, and strict as-of ratings for matchup prediction. Use for team or
  player strength baselines and as features in win/margin models — even if the
  user only says "build Elo" or "power ratings." Includes sports_ds Elo package
  APIs, NFL/NBA/MLB CLI paths, runnable Elo as-of builders, walk-forward
  evaluation, and parameter guidance.
version: "0.6.0"
license: MIT
metadata:
  version: "0.6.0"
---

# Ratings & Strength Models (Sports)

## Overview

Estimate latent team (or player) strength from **past** results, then use those
ratings only as they existed **before** game T.

Ratings are often the strongest simple sports baselines and strong features for
logistic/ML models. The non-negotiable rule: **as-of only**.

Package path:

- `sports_ds.ratings.elo`
- `sports-ds nfl-elo` / `nba-elo` / `mlb-elo`

---

## When to Use This Skill

Use when:

- Team power ratings / rankings over a season
- Matchup priors for win or margin models
- Opponent adjustment
- Strong baselines before feature-heavy ML
- User says “Elo,” “power ratings,” or “team strength”
- NFL/NBA/MLB package Elo baselines

Do **not** use as a substitute for:

| Need | Go to |
|---|---|
| Raw form windows only | `time-series-sports` / `feature-rules` |
| Full ML horse race | `predictive-modeling` |
| Validation design | `validation-design` |
| Season win distributions from ratings | `simulation-sports` |

---

## Installation

```bash
pip install -e .
# multi-sport Elo:
pip install -e ".[multi]"
```

---

## Workflow

1. Choose the **result signal** (win, margin, goal diff, points ratio, EPA, runs).
2. Choose **update style** (sequential Elo-like vs batch season-to-date).
3. Fit/update using **only past games**.
4. Export an **as-of rating** for each team before each game.
5. Predict matchups from rating differentials (+ home).
6. Evaluate with season walk-forward (`validation-design`).
7. Compare to constant / home / form baselines (`baseline-models`).
8. Report params, as-of rule, metrics, limits.
9. Optional: feed into `simulation-sports`.

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

Details: `references/rating_families.md`  
Params: `references/parameters.md`  
Evaluation: `references/evaluation.md`

---

## Elo (package + scripts)

### Package CLI (preferred)

```bash
sports-ds nfl-elo --seasons 2018-2024
sports-ds nba-elo --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-elo --seasons 2023-2024 --min-train-seasons 1 --k 4 --home-adv 20
```

### Skill scripts

```bash
python skills/ratings-strength-models/scripts/elo_asof.py \
  --seasons 2018-2024 \
  --k 20 \
  --home-adv 65 \
  --out data/elo_asof.csv
python skills/ratings-strength-models/scripts/eval_elo_baseline.py --seasons 2018-2024
```

### Python API

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.ratings.elo import add_elo_asof, build_elo_asof_table
from sports_ds.pipelines.team_elo import run_team_elo_baseline

panel = load_team_game_panel(list(range(2018, 2025)))
elo = add_elo_asof(panel, k=20.0, home_adv=65.0)
print(elo[["team", "opponent", "elo_pre", "elo_diff", "won"]].head())

result = run_team_elo_baseline(
    panel, sport="nfl", seasons=list(range(2018, 2025)), min_train_seasons=2
)
print(result["mean_metrics"], result.get("calibration"))
```

Outputs / fields:

- `elo_pre` — team rating before the game
- `opp_elo_pre` — opponent rating before the game
- `elo_diff` — matchup differential including home advantage on the home side
- `elo_expected` — expected score from pre ratings

Code: `src/sports_ds/ratings/elo.py`, `src/sports_ds/pipelines/team_elo.py`

---

## Design Choices

### K factor
- Higher K: reacts faster, noisier
- Lower K: stabler, slower to adapt
- NFL/NBA starting point: K ≈ 20 on 1500-scale Elo
- MLB default in package CLI: lower K (long season)

### Home advantage
- Add `home_adv` to home team pre-game Elo when computing expected score
- Start fixed; estimate later from data if needed

### Margin
- Optional multiplier on K using point differential
- Diminishing returns (log/sqrt) to avoid blowout domination

### Mean reversion / season regression
- Regress ratings toward mean between seasons for multi-year series
- Important for long panels and roster turnover

### Initialization
- Common: all teams 1500
- Report init explicitly

---

## Other Families (patterns)

### Least-squares power ratings (season-to-date)
Each week, solve team strengths from margins-to-date; store as-of ratings before each game. Recompute weekly — never use end-of-season solution for early weeks.

### Offense/defense split
Each team has attack and defense parameters; predict score lines, not only winners. Still as-of only.

### Hierarchical player strength
Partial pooling when player n is uneven (`statistical-modeling` mixed models / Bayesian refs).

---

## Evaluation

**Primary**
- walk-forward log-loss / Brier for win probability from rating diff
- MAE for predicted margin if modeling spreads

**Always compare to**
- constant baseline
- home-only model
- form logistic baseline when available

**Success**
- beats constant on most folds
- preferably competitive with form logistic

---

## Hard Constraints

1. **As-of only** — never use post-game rating to predict that game.
2. Update order must follow real chronology.
3. Do not fit K on the final test season repeatedly without nested validation.
4. Report initialization and scale (e.g. mean 1500).
5. Do not treat ratings as causal player quality without more structure.
6. Package Elo claims must name sport + seasons + params.

---

## Anti-Patterns

- Final rating applied backward to early games
- Huge K chasing noise
- Ignoring home advantage
- Mixing playoffs and regular season without a flag
- Claiming ranking quality without forward prediction metrics
- Using form and Elo interchangeably without a bakeoff

---

## Reporting Template

```text
Rating model: Elo
Sport:
Signal: win (margin multiplier: …)
Params: K=…, home_adv=…, init=1500
As-of rule: pre-game rating before update
Validation: season walk-forward
Metrics vs constant / home / form logistic: …
Calibration:
Limits: no roster continuity, no injuries, …
Reproduce: sports-ds <sport>-elo --seasons ...
```

---

## Output Contract

Done means:

- [ ] As-of rule stated
- [ ] Params stated
- [ ] Walk-forward metrics vs baselines present
- [ ] Limits stated
- [ ] Repro command present

---

## Worked Examples

```bash
sports-ds nfl-elo --seasons 2018-2024 --json-out data/nfl_elo.json
sports-ds nba-elo --seasons 2023-2024 --min-train-seasons 1 --json-out data/nba_elo.json
sports-ds mlb-elo --seasons 2023-2024 --min-train-seasons 1 --json-out data/mlb_elo.json
python skills/ratings-strength-models/scripts/elo_asof.py --seasons 2018-2024 --out data/elo_asof.csv
python skills/simulation-sports/scripts/season_win_sim.py --elo-csv data/elo_asof.csv --season 2024
```

---

## Bundled Resources

### references/
| File | Contents |
|---|---|
| `rating_families.md` | family overview |
| `parameters.md` | K, home_adv, margin, regression |
| `evaluation.md` | how to score ratings |

### scripts/
| File | Contents |
|---|---|
| `elo_asof.py` | build pre-game Elo table |
| `eval_elo_baseline.py` | walk-forward logistic on elo_diff |

### package code
- `src/sports_ds/ratings/elo.py`
- `src/sports_ds/pipelines/team_elo.py`
- `src/sports_ds/pipelines/nfl_elo_baseline.py`
- `src/sports_ds/pipelines/nba_elo_baseline.py`
- `src/sports_ds/pipelines/mlb_elo_baseline.py`

---

## Related Skills

| Need | Skill |
|---|---|
| Baselines | `baseline-models` |
| Features | `feature-rules` |
| Form windows | `time-series-sports` |
| Predictive ML | `predictive-modeling` |
| Validation | `validation-design` |
| Simulation from ratings | `simulation-sports` |

---

## Quick Command Card

```bash
sports-ds nfl-elo --seasons 2018-2024
sports-ds nba-elo --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-elo --seasons 2023-2024 --min-train-seasons 1
python skills/ratings-strength-models/scripts/elo_asof.py --seasons 2018-2024 --out data/elo_asof.csv
python skills/ratings-strength-models/scripts/eval_elo_baseline.py --seasons 2018-2024
python skills/simulation-sports/scripts/season_win_sim.py --elo-csv data/elo_asof.csv --season 2024
```
