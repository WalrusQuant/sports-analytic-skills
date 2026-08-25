---
name: simulation-sports
description: >
  Simulate game and season outcomes from user-supplied probabilities or ratings,
  summarize uncertainty, and test sensitivity to assumptions. Use for standings,
  win totals, matchup distributions, and scenario analysis.
license: MIT
metadata:
  version: "0.12.0"
---

# Simulation (Sports)

## Overview

Turn game-level probabilities or ratings into **distributions**:

- win counts across a declared full-season or remaining-schedule input
- make-playoff-style tallies
- matchup series outcomes
- uncertainty around a point forecast

Simulation does **not** create accuracy the base model lacks — it propagates
uncertainty from a base model under stated assumptions.

Work from user-supplied pre-event probabilities or ratings and a documented schedule.

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

The bundled simulator requires pandas and NumPy:

```bash
python -m pip install pandas numpy
```

Parquet input also needs `pyarrow` or `fastparquet`.

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
| Elo / rating diffs | `ratings-strength-models` or a documented rating artifact |
| Schedule | user-owned event table with stable IDs and roles |

Convert rating diff to probability if needed:

```text
P = 1 / (1 + 10 ** (-elo_diff / 400))
```

If a rating artifact must be converted, document the scale and whether home
advantage is already included. Prefer a probability column whose calibration
has been evaluated on forward holdouts.

## Runnable Schedule-Win Simulator

The helper expects one row per simulated event after filtering, with a
pre-event win probability for the focal team:

```text
season,game_id,is_home,team,opponent,win_probability
```

```bash
python /path/to/simulation-sports/scripts/season_win_sim.py \
  --input schedule_probabilities.parquet \
  --season 2024 --n-sims 5000 --seed 7 --threshold 10 \
  --out season_win_sim_2024.json
```

It filters to `is_home == 1`, requires unique `game_id`, simulates binary
outcomes from the supplied probabilities, aggregates participant wins across
those rows, and writes mean and central quantiles plus optional threshold
probabilities. It does **not** add wins from completed games omitted from the
input. Therefore its output is a full-season total only when the supplied rows
cover every game in that season. For a remaining-schedule projection, add each
team's known completed wins outside this helper and label that external step.
The JSON makes this scope explicit in `win_count_scope` and in canonical fields
such as `mean_wins_in_supplied_games`; ambiguous legacy aliases remain only for
backward compatibility.

### Game-level only

Always simulate one declared perspective per event. Never treat home and away
rows from a symmetric panel as independent games.

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

Read [simulation_assumptions.md](references/simulation_assumptions.md) before fixing event dependence,
schedule, tie, update, or missing-event rules. Read [sensitivity.md](references/sensitivity.md)
when choosing perturbations and deciding whether conclusions are robust.

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
Simulation: wins across supplied full-season / remaining-schedule rows
Base model: Elo→prob (K=…, home_adv=…)
Season:
n_sims: … seed: …
Dependence: independent games | path-dependent rating updates
Outputs: mean and p05/p50/p95 wins in supplied games by team
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
python /path/to/simulation-sports/scripts/season_win_sim.py \
  --input schedule_probabilities.parquet \
  --season 2024 --n-sims 5000 --seed 7 --threshold 10 \
  --out season_win_sim_2024.json
```

Report: “Independent-game Monte Carlo from held-out-calibrated pre-event
probabilities; mean and central quantiles by participant; simulation uncertainty
does not include all roster, injury, schedule, or model uncertainty.”

---

## Bundled Resources

### references/
| File | Contents |
|---|---|
| [simulation_assumptions.md](references/simulation_assumptions.md) | assumption checklist |
| [sensitivity.md](references/sensitivity.md) | what to stress-test |

### scripts/
| File | Contents |
|---|---|
| `season_win_sim.py` | Monte Carlo participant win counts across supplied pre-event probability rows |


---

## Related Skills

| Need | Skill |
|---|---|
| Ratings | `ratings-strength-models` |
| Predictive probs | `predictive-modeling` |
| Calibration | `calibration-check` |
| Reporting | `results-reporting` |
| Rating construction | `ratings-strength-models` |

---

## Quick Command Card

```bash
python /path/to/simulation-sports/scripts/season_win_sim.py \
  --input schedule_probabilities.parquet \
  --season 2024 --n-sims 5000 --seed 7 --threshold 10 \
  --out season_win_sim_2024.json
```

---
