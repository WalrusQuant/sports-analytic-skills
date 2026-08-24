---
name: results-reporting
description: >
  Report sports modeling and analysis results clearly for NFL/NBA/MLB:
  question, data, methods, validation, baselines, metrics, interpretation,
  limits, figures, and repro pointers. Use for notebook summaries, research
  notes, README result sections, and agent final answers after a sports model
  run — even if the user only says "write up the results." Includes a report
  builder from sports_ds pipeline JSON.
version: "0.5.0"
license: MIT
metadata:
  version: "0.5.0"
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

---

## When to Use This Skill

Use when:

- Finished experiment needs a writeup
- Sharing model performance with humans
- Closing an analysis thread cleanly
- Drafting notebook result sections
- Agent needs a final answer format after `sports-ds` runs

Do **not** use when:

- No metrics/baselines yet — run models first
- Need durable model contract docs → also use `model-card`
- Figure honesty review → pair with `anti-slop-analytics`

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

---

## Hard Constraints

1. Never report a model metric without the baseline beside it.
2. Never hide losing folds.
3. Always include n and seasons on key claims.
4. Always include repro commands that match what was run.
5. Distinguish walk-forward from in-sample.
6. If leakage audit was not run, say so.

---

## Anti-Patterns

- Leaderboard screenshot with no method
- “Model is good” without baseline
- Average metrics with no fold table
- Mixing sports without labeling grain
- Writing a novel before the numbers

---

## Output Contract

Done means:

- [ ] Question stated
- [ ] Data/n/period stated
- [ ] Validation design stated
- [ ] Baseline + candidate metrics present
- [ ] Limits present
- [ ] Repro commands present

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

---

## Quick Command Card

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win_pipeline.json
python skills/results-reporting/scripts/render_pipeline_report.py --json data/nfl_win_pipeline.json
sports-ds mlb-elo --seasons 2023-2024 --min-train-seasons 1 --json-out data/mlb_elo.json
python skills/results-reporting/scripts/render_pipeline_report.py --json data/mlb_elo.json --out data/mlb_elo_report.md
```
