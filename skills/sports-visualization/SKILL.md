---
name: sports-visualization
description: >
  Visualization for sports analysis: distributions, form charts, calibration
  plots, matchup graphics, and publication-quality figures that don’t lie.
  Use when exploring or communicating model/data findings.
version: "0.1.0"
license: MIT
---

# Sports Visualization

Plotting and visual analysis skill for sports data science.

## When to use

- EDA plots
- Model diagnostic plots
- Paper/README figures
- Comparing teams/players over time

## When not to use

- No question/metric defined yet
- Decorative dashboard junk with no analytic purpose → `anti-slop-analytics`

## High-value plot types

- season coverage timelines
- target distributions by season
- rolling form with uncertainty
- predicted vs actual / calibration curves
- residual plots by segment
- rating trajectories
- matchup heat / simple 2-way tables

## Procedure

1. State the claim the figure supports.
2. Choose the simplest honest encoding.
3. Label grain, sample size, period.
4. Include baselines where comparison matters.
5. Export reproducible plotting code.
6. Run an anti-slop pass.

## Hard constraints

- Period + n on every key figure
- No truncated axis drama by default
- No dual-axis fake correlation tricks
- Probabilities shown as probabilities, not destiny

## Anti-patterns

- Rainbow spaghetti with 32 teams unlabeled
- 3D junk
- Highlight reels of one hot streak
- Charts without code/repro path

## Output contract

- [ ] Figure purpose stated
- [ ] Code path/repro noted
- [ ] Labels complete
- [ ] Anti-slop check done

## Handoffs

- `eda-sports`
- `anti-slop-analytics`
- `results-reporting`
- `calibration-check`

## Stack hints

- Python: matplotlib, (optional) seaborn/plotnine
- Keep dependencies light unless user wants more
