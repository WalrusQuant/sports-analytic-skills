---
name: sports-visualization
description: >
  Visualization for sports analysis across NFL/NBA/MLB panels: distributions,
  form charts, calibration plots, rating trajectories, walk-forward metric
  bars, and publication-quality figures that do not lie. Use when exploring or
  communicating model/data findings — even if the user only says "plot this" or
  "make a chart." Includes plot catalog, honest-label rules, multi-sport
  scripts, and pipeline-JSON charting wired to sports_ds.
version: "0.6.0"
license: MIT
metadata:
  version: "0.6.0"
---

# Sports Visualization

## Overview

Plotting and visual analysis skill for sports data science.

Every key figure needs:

- period
- n
- metric definition
- sport/grain when not obvious
- a baseline when comparing models

Prefer package data (`sports_ds` panels) and pipeline JSON over mystery CSV dumps
so figures stay reproducible.

This skill draws honest figures. `anti-slop-analytics` judges whether they still lie.

---

## When to Use This Skill

Use when:

- EDA plots
- Model diagnostic plots
- Paper/README figures
- Comparing teams/players over time
- User says “plot this” or “make a chart”
- Building walk-forward metric charts from pipeline JSON

Do **not** use when:

| Need | Go instead |
|---|---|
| No question/metric defined yet | `sports-modeling-doctrine` / `eda-sports` |
| Decorative dashboard junk | `anti-slop-analytics` (kill it) |
| Full results writeup | `results-reporting` |
| Probability reliability deep-dive | `calibration-check` |

---

## Installation

```bash
pip install -e .
# optional
pip install seaborn
```

Multi-sport panels:

```bash
pip install -e ".[multi]"
```

---

## High-Value Plot Types

| Plot | Use | sports_ds source |
|---|---|---|
| Coverage timeline | seasons/weeks present | team-game panel |
| Target histogram | margin/score distribution | `point_diff` / scores |
| Home advantage bar | home win rate by season | `is_home==1` rows |
| Form line | rolling/EWMA trajectory | shifted form features |
| Calibration curve | prob reliability | calibrate JSON / probs |
| Residual scatter | margin model fit | margin preds |
| Rating trajectory | Elo/power over time | `elo_asof` table |
| Walk-forward metric bars | model vs baseline | pipeline JSON folds |

Catalog: `references/plot_catalog.md`  
Label rules: `references/honest_labels.md`

---

## Workflow

1. State the claim the figure supports.
2. Load data via `sports_ds` (or pipeline JSON), not mystery screenshots.
3. Choose the simplest honest encoding.
4. Label grain, sample size, period, sport.
5. Include baselines where comparison matters.
6. Export reproducible plotting code + output path.
7. Run an anti-slop pass (`anti-slop-analytics`).
8. If used in a claim, store path + command in experiment log.

---

## Scripts

```bash
# NFL defaults
python skills/sports-visualization/scripts/plot_home_margin_hist.py --seasons 2023-2024
python skills/sports-visualization/scripts/plot_home_win_rate.py --seasons 2018-2024

# multi-sport when [multi] installed
python skills/sports-visualization/scripts/plot_home_win_rate.py --sport nba --seasons 2023-2024
python skills/sports-visualization/scripts/plot_home_margin_hist.py --sport mlb --seasons 2023-2024
python skills/sports-visualization/scripts/plot_walkforward_metrics.py \
  --json data/nba_win_pipeline.json --metric logistic_log_loss --baseline constant_log_loss
```

Generate pipeline JSON first:

```bash
sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1 --json-out data/nba_win_pipeline.json
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win_pipeline.json
sports-ds mlb-elo --seasons 2023-2024 --min-train-seasons 1 --json-out data/mlb_elo.json
```

---

## Encoding Defaults

| Comparison | Prefer |
|---|---|
| Rates over seasons | bars/lines with n annotated |
| Model vs baseline | grouped bars or paired table |
| Distributions | histogram/density + mean/median line |
| Probabilities | reliability curve, not pie |
| Rankings | ordered dots, not rainbow spaghetti |

Default y-axis for win rates: full enough to avoid drama (do not start at 0.55).

---

## Hard Constraints

1. Period + n on every key figure.
2. No truncated axis drama by default.
3. No dual-axis fake correlation tricks.
4. Probabilities shown as probabilities, not destiny.
5. Repro path required for any figure used in a claim.
6. Sport/grain labeled when not obvious.
7. Walk-forward figures must not be labeled as in-sample fit.

---

## Anti-Patterns

- Rainbow spaghetti with 30 teams unlabeled
- 3D junk
- Highlight reels of one hot streak
- Charts without code/repro path
- Missing baselines on model comparisons
- Plotting in-sample fit as validation
- Cropping axes to manufacture home-field drama

---

## Output Contract

Done means:

- [ ] Figure purpose stated
- [ ] Code path/repro noted
- [ ] Labels complete (period, n, metric, sport)
- [ ] Baseline present when claim is comparative
- [ ] Anti-slop check done

---

## Worked Examples

### Home win rate
```bash
python skills/sports-visualization/scripts/plot_home_win_rate.py \
  --sport nfl --seasons 2018-2024 --out data/nfl_home_wr.png
```
Caption must include seasons + n games + “home rows only”.

### Walk-forward model vs baseline
```bash
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win.json
python skills/sports-visualization/scripts/plot_walkforward_metrics.py \
  --json data/nfl_win.json \
  --metric logistic_log_loss \
  --baseline constant_log_loss \
  --out data/nfl_wf.png
python skills/anti-slop-analytics/scripts/figure_audit_template.py --out data/nfl_wf_audit.md
```

---

## Bundled Resources

### references/
- `plot_catalog.md`
- `honest_labels.md`

### scripts/
- `plot_home_margin_hist.py`
- `plot_home_win_rate.py`
- `plot_walkforward_metrics.py`

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
python skills/sports-visualization/scripts/plot_home_win_rate.py --sport nba --seasons 2023-2024
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win_pipeline.json
python skills/sports-visualization/scripts/plot_walkforward_metrics.py --json data/nfl_win_pipeline.json
```
