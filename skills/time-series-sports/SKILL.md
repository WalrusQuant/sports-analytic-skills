---
name: time-series-sports
description: >
  Time-series and form modeling for sports: rolling performance, recency
  weighting, seasonality/regime shifts, and forecasting player or team form.
  Use when history order and recent form matter.
version: "0.1.0"
license: MIT
---

# Time Series & Form (Sports)

Skill for ordered sports performance over time.

## When to use

- Team/player form features
- Rolling averages, EWMA, decay
- Forecasting next-game stats from trajectories
- Handling bye weeks, injuries gaps, season breaks

## When not to use

- Cross-sectional only models with no recency component
- Static season aggregates already sufficient

## Core techniques

- expanding / rolling windows ending before T
- exponential decay / half-life form
- rest-day adjustments
- season phase indicators
- regime splits (rule changes, coaching eras)
- simple state-space / dynamic ratings handoff

## Procedure

1. Define the series entity and frequency (game, week, day).
2. Align timestamps; handle missing games explicitly.
3. Choose window/decay hyperparameters on training folds only.
4. Ensure all form features use data strictly before T.
5. Compare form features against static baselines.
6. Watch for small-sample explosions early season.

## Hard constraints

- No centered rolling windows that peek forward
- No “season average including current game”
- Early-season priors/shrinkage required when n is tiny
- Validate across seasons, not one hot streak

## Anti-patterns

- Fixed 5-game mean with no shrinkage
- Ignoring opponent strength in raw form
- Treating playoffs and regular season as identical without check

## Output contract

- [ ] Series definition + frequency
- [ ] Window/decay rules
- [ ] Time-safety confirmed
- [ ] Comparison vs non-form baseline
- [ ] Failure modes (early season, injuries)

## Handoffs

- `ratings-strength-models` for opponent-adjusted strength
- `feature-rules`
- `predictive-modeling`
- `eda-sports`
