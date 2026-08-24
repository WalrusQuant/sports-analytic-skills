---
name: ratings-strength-models
description: >
  Build and evaluate sports strength/rating models (Elo-like, mass-transfer,
  offense/defense splits, basic power ratings). Use for team/player strength
  baselines and matchup prediction inputs.
version: "0.1.0"
license: MIT
---

# Ratings & Strength Models

Core sports-analytics skill for latent strength estimation.

## When to use

- Team power ratings
- Matchup priors for game prediction
- Opponent adjustment
- Strong baselines before feature-heavy ML

## When not to use

- Pitch-level baseball micro-models as first step
- Pure counting-stat leaderboards with no opponent context

## Model families

| Family | Notes |
|---|---|
| Elo / Glicko-style | sequential updates, margin optional |
| Offense/defense split ratings | score models, possessions |
| Least-squares power ratings | season-to-date systems of equations |
| Regularized hierarchical strength | partial pooling players/teams |
| Possession/resource models | sport-specific later modules |

## Procedure

1. Define result signal (win, goal diff, points ratio, EPA, runs, etc.).
2. Choose update style (sequential vs batch season-to-date).
3. Set home advantage and mean-reversion/shrinkage.
4. Produce pre-event ratings only (as-of T).
5. Convert ratings to matchup features or probabilities.
6. Evaluate vs base rates on walk-forward.

## Hard constraints

- Ratings used at T may only include results before T
- Home advantage estimated, not vibes-only forever
- Compare rating model to naive base rates
- Document initialization and k-factors / shrinkage

## Anti-patterns

- Using final-season ratings to “predict” that season’s early games
- No home parameter in leagues where home matters
- Updating with future games because the loop was written carelessly

## Output contract

- [ ] Rating definition + update rule
- [ ] As-of logic stated
- [ ] Home/shrinkage choices
- [ ] Predictive metrics vs baselines
- [ ] Exportable pre-event rating table

## Handoffs

- `baseline-models`
- `statistical-modeling` / `predictive-modeling`
- `simulation-sports`
- `feature-rules`
