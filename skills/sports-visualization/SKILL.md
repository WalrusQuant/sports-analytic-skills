---
name: sports-visualization
description: >
  Visualization for sports analysis: distributions, form charts, calibration
  plots, rating trajectories, matchup graphics, and publication-quality figures
  that do not lie. Use when exploring or communicating model/data findings —
  even if the user only says "plot this" or "make a chart." Includes plot
  catalog, honest-label rules, and runnable histogram scripts.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# Sports Visualization

## Overview

Plotting and visual analysis skill for sports data science.

Every key figure needs: **period, n, metric definition**, and a baseline when comparing models.

---

## When to Use This Skill

Use when:

- EDA plots
- Model diagnostic plots
- Paper/README figures
- Comparing teams/players over time
- User says “plot this” or “make a chart”

Do **not** use when:

- No question/metric defined yet
- Decorative dashboard junk with no analytic purpose → `anti-slop-analytics`

---

## Installation

```bash
pip install -e .
# optional
pip install seaborn
```

---

## High-Value Plot Types

| Plot | Use |
|---|---|
| Coverage timeline | seasons/weeks present |
| Target histogram | margin/score distribution |
| Home advantage bar | home win rate by season |
| Form line | rolling/EWMA trajectory |
| Calibration curve | prob reliability |
| Residual scatter | margin model fit |
| Rating trajectory | Elo/power over time |
| Walk-forward metric table/bars | model vs baseline |

Catalog: `references/plot_catalog.md`  
Label rules: `references/honest_labels.md`

---

## Workflow

1. State the claim the figure supports.
2. Choose the simplest honest encoding.
3. Label grain, sample size, period.
4. Include baselines where comparison matters.
5. Export reproducible plotting code.
6. Run an anti-slop pass (`anti-slop-analytics`).

---

## Scripts

```bash
python skills/sports-visualization/scripts/plot_home_margin_hist.py --seasons 2023-2024
python skills/sports-visualization/scripts/plot_home_win_rate.py --seasons 2018-2024
```

---

## Hard Constraints

1. Period + n on every key figure.
2. No truncated axis drama by default.
3. No dual-axis fake correlation tricks.
4. Probabilities shown as probabilities, not destiny.
5. Repro path required for any figure used in a claim.

---

## Anti-Patterns

- Rainbow spaghetti with 32 teams unlabeled
- 3D junk
- Highlight reels of one hot streak
- Charts without code/repro path
- Missing baselines on model comparisons

---

## Output Contract

- [ ] Figure purpose stated
- [ ] Code path/repro noted
- [ ] Labels complete (period, n, metric)
- [ ] Anti-slop check done

---

## Bundled Resources

### references/
- `plot_catalog.md`
- `honest_labels.md`

### scripts/
- `plot_home_margin_hist.py`
- `plot_home_win_rate.py`

---

## Related Skills

- `eda-sports`
- `anti-slop-analytics`
- `results-reporting`
- `calibration-check`
- `model-interpretation`

---

## Quick Command Card

```bash
python skills/sports-visualization/scripts/plot_home_margin_hist.py --seasons 2023-2024
python skills/sports-visualization/scripts/plot_home_win_rate.py --seasons 2018-2024
```
