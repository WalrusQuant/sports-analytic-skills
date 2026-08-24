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

# Sports Simulation

## Outcome

Produce a reproducible distribution of outcomes, not a single-point forecast.
Inputs must be user-owned probability or rating artifacts with documented timing,
calibration evidence, schedule coverage, and assumptions.

## Required inputs

- one row per simulated event
- stable event and participant identifiers
- event time and season
- home/away or equivalent roles
- pre-event win probability, or a rating difference with a declared conversion
- number of simulations and random seed
- dependence, tie, update, and schedule assumptions

## Workflow

1. Validate that each event appears once and all probabilities are finite in `[0, 1]`.
2. Confirm inputs were available before each simulated event.
3. Check probability calibration on an appropriate held-out sample.
4. Define ties, cancellations, neutral sites, and missing events.
5. Choose whether events are conditionally independent or correlated.
6. Draw outcomes with a fixed seed and aggregate to the desired season statistic.
7. Report mean, median, quantiles, and threshold probabilities.
8. Rerun with multiple seeds and plausible parameter perturbations.
9. Save input fingerprint, assumptions, configuration, and output artifact.

## Rating conversion

For Elo-like differences on the conventional 400-point scale:

```python
p_home = 1 / (1 + 10 ** (-elo_diff / 400))
```

Use this only when `elo_diff` already includes any home advantage intended by the
rating definition. Do not add it twice.

## Independence and updates

Independent Bernoulli draws are a transparent baseline. Shared injuries,
weather, latent team strength, or qualification incentives may induce dependence.
If ratings update inside a simulated season, specify the update order and prevent
simulated future information from leaking into earlier events.

## Input schema for bundled helper

CSV, Parquet, or JSON columns:

```text
season,game_id,is_home,team,opponent,win_probability
```

After filtering to `is_home == 1`, `game_id` must be unique and each row's
`win_probability` is the focal team's pre-event win probability.

```bash
python <path-to-simulation-sports>/scripts/season_win_sim.py \
  --input data/schedule_probabilities.parquet \
  --season 2024 \
  --n-sims 5000 \
  --seed 7 \
  --threshold 10 \
  --out data/season_win_sim.json
```

## Hard constraints

- Never simulate from in-sample probabilities presented as future estimates.
- Never omit the random seed or number of draws.
- Never report expected wins without a distribution.
- Never assume independence without disclosure.
- Never silently drop games or teams.
- Never present simulation uncertainty as total real-world uncertainty.

## Output contract

Return input artifact and fingerprint, event count, participant count, simulation
count, seed, assumptions, mean and central quantiles by participant, threshold
probabilities, sensitivity results, and known omitted uncertainty.

## Resources

- `references/simulation_assumptions.md` — assumption checklist
- `references/sensitivity.md` — perturbation design
- `scripts/season_win_sim.py` — validated probability-based season simulator
