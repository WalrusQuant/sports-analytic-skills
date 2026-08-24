---
name: simulation-sports
description: >
  Simulation for sports analysis: game simulations from rating/probability
  models, season win-total projections, playoff-path style uncertainty, and
  Monte Carlo summaries. Use after a predictive or rating model exists and you
  need distributional outcomes. Includes a runnable season win simulator from
  as-of Elo / probability inputs.
version: "0.3.0"
license: MIT
metadata:
  version: "0.3.0"
---

# Simulation (Sports)

## Overview

Turn game-level probabilities or ratings into **distributions**: season wins,
make-playoff-style tallies, matchup series outcomes. Simulation does not create
accuracy the base model lacks — it propagates uncertainty.

## When to Use This Skill

- Season win-total distributions
- Playoff-path / remaining-schedule projections from a model
- Matchup simulations from ratings or predictive probabilities
- Stress-testing uncertainty around a point forecast

## When Not to Use

- No underlying probability/rating model yet → build one first
- Single-point prediction is enough
- Discrete-event engineering sims unrelated to sports outcomes

---

## Installation

```bash
pip install -e .
```

---

## Workflow

1. **Define the object** being simulated (game, series, rest-of-season).
2. **Choose the base model** (logistic probs, Elo expected score, etc.).
3. **State dependence assumptions** (independent games? injury freeze? home effects?).
4. **Fix seeds and n_sims** for reproducibility.
5. **Run Monte Carlo**.
6. **Summarize distributions** (mean, median, p05/p95, full histogram) — not only means.
7. **Sensitivity-check** K, home advantage, independence assumptions.

---

## Base Model Inputs

| Input | Source skill / code |
|---|---|
| Pre-game win probs | `predictive-modeling`, `statistical-modeling`, `baseline-models` |
| Elo / rating diffs | `ratings-strength-models` (`elo_asof.py`) |
| Schedule panel | `sports_ds.data.nfl.load_team_game_panel` / schedules |

Convert rating diff to probability if needed:

```text
P(home) = 1 / (1 + 10 ** (-elo_diff / 400))
```

(with home advantage already inside `elo_diff` if using the bundled Elo script)

---

## Runnable Season Simulator

```bash
# build Elo as-of, then simulate remaining-style season win totals from game probs
python skills/ratings-strength-models/scripts/elo_asof.py --seasons 2023-2024 --out data/elo_asof.csv
python skills/simulation-sports/scripts/season_win_sim.py \
  --elo-csv data/elo_asof.csv \
  --season 2024 \
  --n-sims 5000 \
  --seed 7 \
  --out data/season_win_sim_2024.json
```

What it does:

1. loads as-of Elo rows for one season
2. converts each team-game `elo_diff` to a win probability
3. Monte Carlo simulates binary outcomes independently given those probs
4. aggregates win totals per team across sims
5. writes mean/p05/p50/p95 win totals

---

## Design Choices

### Independence

Default script treats games as conditionally independent given pre-game probs.
That understates variance if injuries/momentum couple games. State the shortcut.

### Updating ratings inside the season sim

Simple mode: freeze pre-game probs from historical as-of table (reproducible evaluation).  
Advanced mode: update Elo inside each simulated world (path-dependent). Start simple.

### Schedule constraints

Season sims must use the real schedule graph (each game once). Do not double-count team-game panel rows — simulate on **game-level** home rows only.

---

## Hard Constraints

1. Simulation cannot invent accuracy the base model lacks.
2. Report seeds, n_sims, and assumptions every time.
3. Do not present simulated means as guarantees.
4. Respect schedule constraints.
5. If base probs are miscalibrated, fix/note calibration first (`calibration-check`).

---

## Anti-Patterns

- Simulating with an unvalidated coin-flip model dressed as analysis
- Huge n_sims hiding bad assumptions
- Showing only expected wins with no spread
- Using both home and away panel rows as two independent games

---

## Reporting Template

```text
Simulation: rest-of-season / full-season win totals
Base model: Elo→prob (K=…, home_adv=…)
Season: …
n_sims: … seed: …
Dependence: independent games | path-dependent rating updates
Outputs: mean wins, p05/p50/p95 by team
Sensitivity: …
Limits: …
```

---

## Bundled Resources

### scripts/

- `season_win_sim.py` — Monte Carlo team win totals from Elo as-of table

### references/

- `simulation_assumptions.md`

### related package / skills

- `skills/ratings-strength-models/scripts/elo_asof.py`
- `predictive-modeling`, `calibration-check`, `results-reporting`

---

## Related Skills

- Ratings: `ratings-strength-models`
- Predictive probs: `predictive-modeling`
- Calibration: `calibration-check`
- Reporting: `results-reporting`
