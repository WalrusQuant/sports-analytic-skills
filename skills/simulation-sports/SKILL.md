---
name: simulation-sports
description: >
  Simulation for sports analysis: game simulations from rating or probability
  models, season win-total projections, playoff-path style uncertainty, Monte
  Carlo summaries, and sensitivity checks. Use after a predictive or rating
  model exists and you need distributional outcomes — even if the user only
  says "project the standings" or "simulate the season." Includes a runnable
  season win simulator from as-of Elo inputs, package Elo CLI paths for
  NFL/NBA/MLB, assumption checklists, and reporting templates.
version: "0.6.0"
license: MIT
metadata:
  version: "0.6.0"
---

# Simulation (Sports)

## Overview

Turn game-level probabilities or ratings into **distributions**:

- season win totals
- make-playoff-style tallies
- matchup series outcomes
- uncertainty around a point forecast

Simulation does **not** create accuracy the base model lacks — it propagates
uncertainty from a base model under stated assumptions.

Stack: `sports_ds` Elo / win probs + Monte Carlo scripts.

---

## When to Use This Skill

Use when:

- Season win-total distributions
- Playoff-path / remaining-schedule projections from a model
- Matchup simulations from ratings or predictive probabilities
- Stress-testing uncertainty around a point forecast
- User says “project the standings” or “simulate the season”

Do **not** use when:

| Need | Go instead |
|---|---|
| No underlying probability/rating model yet | build one first (`ratings-strength-models`, `predictive-modeling`) |
| Single-point prediction is enough | modeling skills only |
| Discrete-event engineering sims unrelated to sports outcomes | out of scope |
| Calibration of the base probs | `calibration-check` first |

---

## Installation

```bash
pip install -e .
# multi-sport Elo inputs:
pip install -e ".[multi]"
```

---

## Required Inputs

- Base model: pre-game win probs or as-of rating differentials
- Schedule / remaining games (one row per game, not doubled panel)
- n_sims and seed
- Dependence assumption (independent games vs path-dependent updates)
- Sport + season window

---

## Workflow

1. **Define the object** being simulated (game, series, rest-of-season, full season).
2. **Choose the base model** (logistic probs, Elo expected score, etc.).
3. **Confirm base probs are at least usable** (`calibration-check` if quoting percents).
4. **State dependence assumptions** (independent games? injury freeze? home effects?).
5. **Fix seeds and n_sims** for reproducibility.
6. **Build as-of inputs** (Elo table or probability table).
7. **Run Monte Carlo on home rows once per game**.
8. **Summarize distributions** (mean, median, p05/p95, histogram) — not only means.
9. **Sensitivity-check** K, home advantage, independence assumptions.
10. **Report** seeds, n_sims, assumptions, limits, repro commands.

---

## Base Model Inputs

| Input | Source |
|---|---|
| Pre-game win probs | `predictive-modeling`, `statistical-modeling`, `baseline-models` |
| Elo / rating diffs | `ratings-strength-models`, `sports-ds *-elo` |
| Schedule panel | `sports_ds.data.*` / schedules |

Convert rating diff to probability if needed:

```text
P = 1 / (1 + 10 ** (-elo_diff / 400))
```

Package Elo paths:

```bash
sports-ds nfl-elo --seasons 2018-2024 --json-out data/nfl_elo.json
sports-ds nba-elo --seasons 2023-2024 --min-train-seasons 1 --json-out data/nba_elo.json
sports-ds mlb-elo --seasons 2023-2024 --min-train-seasons 1 --json-out data/mlb_elo.json
python skills/ratings-strength-models/scripts/elo_asof.py --seasons 2023-2024 --out data/elo_asof.csv
```

---

## Runnable Season Simulator

```bash
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

### Game-level only

Always simulate on **home rows once per game**. Never treat home and away panel rows as two independent games.

---

## Design Choices

### Independence
Default script treats games as conditionally independent given pre-game probs.
That understates variance if injuries/momentum couple games. **State the shortcut.**

### Updating ratings inside the season sim
- **Simple mode:** freeze pre-game probs from historical as-of table (reproducible evaluation)
- **Advanced mode:** update Elo inside each simulated world (path-dependent)

Start simple.

### Schedule constraints
Season sims must use the real schedule graph. One game once.

### Calibration prerequisite
If base probs are miscalibrated, fix/note calibration first (`calibration-check`).

See `references/simulation_assumptions.md` and `references/sensitivity.md`.

---

## Hard Constraints

1. Simulation cannot invent accuracy the base model lacks.
2. Report seeds, n_sims, and assumptions every time.
3. Do not present simulated means as guarantees.
4. Respect schedule constraints.
5. If base probs are miscalibrated, say so.
6. Never double-count home and away panel rows as two games.
7. Sensitivity is required before strong distribution claims.

---

## Anti-Patterns

- Simulating with an unvalidated coin-flip model dressed as analysis
- Huge n_sims hiding bad assumptions
- Showing only expected wins with no spread
- Using both home and away panel rows as two independent games
- Silent dependence assumptions
- Quoting playoff odds from uncalibrated 0.55-ish probs

---

## Reporting Template

```text
Simulation: rest-of-season / full-season win totals
Base model: Elo→prob (K=…, home_adv=…)
Season:
n_sims: … seed: …
Dependence: independent games | path-dependent rating updates
Outputs: mean wins, p05/p50/p95 by team
Sensitivity:
Limits:
Reproduce:
```

---

## Output Contract

Done means:

- [ ] Base model named and sourced
- [ ] n_sims + seed reported
- [ ] Dependence assumption stated
- [ ] Distribution summaries (not only means)
- [ ] Sensitivity note present
- [ ] Repro commands present

---

## Worked Example

```bash
python skills/ratings-strength-models/scripts/elo_asof.py --seasons 2024 --out data/elo_asof.csv
python skills/simulation-sports/scripts/season_win_sim.py \
  --elo-csv data/elo_asof.csv --season 2024 --n-sims 5000 --seed 7 \
  --out data/season_win_sim_2024.json
```

Report: “Independent-game Monte Carlo from as-of Elo probs; mean and p05/p95
win totals by team; not a claim the Elo model is well-calibrated unless checked.”

---

## Bundled Resources

### references/
| File | Contents |
|---|---|
| `simulation_assumptions.md` | assumption checklist |
| `sensitivity.md` | what to stress-test |

### scripts/
| File | Contents |
|---|---|
| `season_win_sim.py` | Monte Carlo team win totals from Elo as-of table |

### related
- `skills/ratings-strength-models/scripts/elo_asof.py`
- `predictive-modeling`, `calibration-check`, `results-reporting`

---

## Related Skills

| Need | Skill |
|---|---|
| Ratings | `ratings-strength-models` |
| Predictive probs | `predictive-modeling` |
| Calibration | `calibration-check` |
| Reporting | `results-reporting` |
| Package Elo CLI | `sports-ds nfl-elo` / `nba-elo` / `mlb-elo` |

---

## Quick Command Card

```bash
python skills/ratings-strength-models/scripts/elo_asof.py --seasons 2024 --out data/elo_asof.csv
python skills/simulation-sports/scripts/season_win_sim.py --elo-csv data/elo_asof.csv --season 2024 --n-sims 5000
sports-ds nfl-elo --seasons 2018-2024
sports-ds nba-elo --seasons 2023-2024 --min-train-seasons 1
```
