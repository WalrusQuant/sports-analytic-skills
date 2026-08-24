---
name: results-reporting
description: >
  Report sports modeling and analysis results clearly for NFL/NBA/MLB:
  question, data, methods, validation, baselines, metrics, interpretation,
  limits, figures, and repro pointers. Use for notebook summaries, research
  notes, README result sections, and agent final answers after a sports model
  run — even if the user only says "write up the results." Includes a report
  builder from sports_ds pipeline JSON and multi-sport command patterns.
version: "0.6.0"
license: MIT
metadata:
  version: "0.6.0"
---

# Results Reporting (Sports)

## Overview

Turn a finished sports analysis into a writeup a stranger can trust:

- question
- methods
- baselines
- numbers
- limits
- repro

No hype. No missing baseline.

Works with `sports-ds` pipeline JSON from NFL/NBA/MLB win, margin, and Elo paths.

A results report is the human-readable story of one evaluation. A model card is
the frozen operating contract. An experiment log is the trial history.

---

## When to Use This Skill

Use when:

- Finished experiment needs a writeup
- Sharing model performance with humans
- Closing an analysis thread cleanly
- Drafting notebook result sections
- Agent needs a final answer format after `sports-ds` runs

Do **not** use when:

| Need | Go instead |
|---|---|
| No metrics/baselines yet | run models first |
| Durable model contract | `model-card` |
| Figure honesty review | `anti-slop-analytics` |
| Trial history / decisions | `experiment-log` |
| Why misses happened | `model-interpretation` |

---

## Installation

```bash
pip install -e .
# multi-sport:
pip install -e ".[multi]"
```

---

## Required Structure

Every sports results writeup includes:

1. **Question**
2. **Data** — sport, source, grain, period, n
3. **Methods / models**
4. **Validation design**
5. **Baselines + results**
6. **Interpretation**
7. **Limits / next tests**
8. **Repro pointers** (commands, scripts, seeds, package versions)

Skip hype. Lead with question and metric.

Checklist: `references/writeup_checklist.md`  
Templates: `references/templates.md`

---

## Workflow

1. Collect artifacts (pipeline JSON, metrics tables, plots, commit hash).
2. Fill the structure above in order.
3. Put baseline comparisons next to candidate metrics — never alone.
4. State sample sizes and seasons on every key number.
5. Separate what the model *predicts* from what it *explains*.
6. List limits explicitly.
7. Link exact commands to reproduce.
8. Optional: anti-slop pass on figures.
9. Optional: promote `keep` results into a model card.

---

## Generate a draft from pipeline output

```bash
# NFL win
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win_pipeline.json
python skills/results-reporting/scripts/render_pipeline_report.py \
  --json data/nfl_win_pipeline.json \
  --out data/nfl_win_report.md

# NBA win
sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1 --json-out data/nba_win.json
python skills/results-reporting/scripts/render_pipeline_report.py \
  --json data/nba_win.json \
  --out data/nba_win_report.md

# MLB margin
sports-ds mlb-margin-pipeline --seasons 2023-2024 --min-train-seasons 1 --json-out data/mlb_margin.json
python skills/results-reporting/scripts/render_pipeline_report.py \
  --json data/mlb_margin.json \
  --out data/mlb_margin_report.md

# Elo baseline
sports-ds nba-elo --seasons 2023-2024 --min-train-seasons 1 --json-out data/nba_elo.json
python skills/results-reporting/scripts/render_pipeline_report.py \
  --json data/nba_elo.json \
  --out data/nba_elo_report.md
```

After draft generation, edit interpretation/limits by hand. Do not ship the raw template if folds are ugly.

---

## Metric Presentation Rules

| Target | Show |
|---|---|
| Win probs | log-loss + baseline log-loss; Brier/ECE if available |
| Margin | MAE/RMSE + constant baseline |
| Elo baseline | elo logistic log-loss vs constant |
| Any claim | per-fold table, not only means |

Never lead with accuracy alone.

---

## Hard Constraints

1. Never report a model metric without the baseline beside it.
2. Never hide losing folds.
3. Always include n and seasons on key claims.
4. Always include repro commands that match what was run.
5. Distinguish walk-forward from in-sample.
6. If leakage audit was not run, say so.
7. If calibration was not run for probability claims, say so.

---

## Anti-Patterns

- Leaderboard screenshot with no method
- “Model is good” without baseline
- Average metrics with no fold table
- Mixing sports without labeling grain
- Writing a novel before the numbers
- Quietly dropping the season that lost

---

## Output Contract

Done means:

- [ ] Question stated
- [ ] Data/n/period stated
- [ ] Validation design stated
- [ ] Baseline + candidate metrics present
- [ ] Per-fold or per-season evidence present
- [ ] Limits present
- [ ] Repro commands present

---

## Worked Example

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win.json
python skills/results-reporting/scripts/render_pipeline_report.py --json data/nfl_win.json --out data/nfl_win_report.md
python skills/sports-visualization/scripts/plot_walkforward_metrics.py --json data/nfl_win.json --out data/nfl_wf.png
python skills/anti-slop-analytics/scripts/figure_audit_template.py --out data/nfl_fig_audit.md
```

Writeup lead:

> Pre-game NFL team-win logistic on shifted form features beat constant train-rate
> log-loss under season walk-forward 2018–2024. Leakage audit CLEAN. Limits: no
> injury model; early-season cold start.

---

## Bundled Resources

### references/
- `templates.md`
- `writeup_checklist.md`

### scripts/
- `render_pipeline_report.py`

---

## Related Skills

- `model-card`
- `experiment-log`
- `anti-slop-analytics`
- `model-interpretation`
- `validation-design`
- `baseline-models`
- `calibration-check`

---

## Quick Command Card

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win_pipeline.json
python skills/results-reporting/scripts/render_pipeline_report.py --json data/nfl_win_pipeline.json
sports-ds mlb-elo --seasons 2023-2024 --min-train-seasons 1 --json-out data/mlb_elo.json
python skills/results-reporting/scripts/render_pipeline_report.py --json data/mlb_elo.json --out data/mlb_elo_report.md
```
