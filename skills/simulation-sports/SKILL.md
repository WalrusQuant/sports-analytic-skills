---
name: simulation-sports
description: >
  Simulation for sports analysis: game simulations from rating/probability
  models, season projections, and uncertainty via Monte Carlo. Use after a
  predictive model exists and you need distributional outcomes.
version: "0.1.0"
license: MIT
---

# Simulation (Sports)

Simulation skill for projecting games/seasons and quantifying uncertainty.

## When to use

- Season win-total distributions
- Playoff odds style projections from a model
- Matchup simulations from ratings or predictive probs
- Stress-testing model uncertainty

## When not to use

- No underlying probability/rating model yet
- Single-point prediction is enough
- Discrete-event engineering sims unrelated to sports outcomes

## Procedure

1. Define what is being simulated (game, series, season).
2. Use a validated predictive model or rating→probability map.
3. Specify dependence assumptions (injuries, schedule, independence shortcuts).
4. Run Monte Carlo with fixed seeds for repro.
5. Summarize distributions, not only means.
6. Sensitivity-check key assumptions.

## Hard constraints

- Simulation cannot invent accuracy the base model lacks
- Report seeds, n_sims, and assumptions
- Do not present simulated means as guarantees
- Schedule constraints must be respected for season sims

## Anti-patterns

- Simulating with an unvalidated toy coin-flip model dressed as analysis
- Huge n_sims hiding bad assumptions
- Ignoring variance / showing only expected wins

## Output contract

- [ ] Base model identified
- [ ] Assumptions listed
- [ ] n_sims + seed
- [ ] Distribution summaries
- [ ] Sensitivity notes

## Handoffs

- `ratings-strength-models` / `predictive-modeling`
- `results-reporting`
- `model-interpretation`
