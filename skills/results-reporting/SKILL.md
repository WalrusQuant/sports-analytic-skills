---
name: results-reporting
description: >
  Report sports modeling and analysis results clearly: question, data, methods,
  validation, baselines, metrics, interpretation, limits, figures, and repro
  pointers. Use for notebook summaries, research notes, README result sections,
  and agent final answers after a sports model run — even if the user only says
  "write up the results." Includes a report builder from sports_ds pipeline JSON.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
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
```

---

## Required Structure

Every sports results writeup includes:

1. **Question**
2. **Data** — source, grain, period, n
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

---

## Generate a draft from pipeline output

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win_pipeline.json
python skills/results-reporting/scripts/render_pipeline_report.py \
  --json data/nfl_win_pipeline.json \
  --out data/nfl_win_report.md
```

---

## Metric Presentation Rules

| Do | Don't |
|---|---|
| Primary metric first | Lead with accuracy only |
| Show baseline beside model | Model metric in isolation |
| Per-season + mean | One pooled number hiding bad years |
| n and period | Orphan percentages |
| “did not beat baseline” when true | Silent omission of failures |

---

## Hard Constraints

1. Lead with the question and metric, not hype.
2. Always include baselines when performance is claimed.
3. Always include period and sample size.
4. Unknowns stay unknown — do not invent.
5. Do not present in-sample fits as validation.

---

## Anti-Patterns

- Metric dump without method
- Hidden filters / silent row drops
- “Model works” with no baseline
- Screenshots without repro
- Cherry-picked best season as the headline

---

## Writeup Template

```markdown
# Results: <title>

## Question
…

## Data
Source: …
Grain: …
Period: …
n: …

## Methods
Models: …
Features: …
Decision time T: …

## Validation
Design: season walk-forward …
Primary metric: …

## Results
| Model | Mean metric | Notes |
|---|---:|---|
| constant | … | |
| logistic | … | |

Per-season: …

## Interpretation
…

## Limits
…

## Reproduce
```bash
…
```
```

---

## Worked Example (NFL win pipeline)

```text
Question: Pre-game P(team win) on NFL team-game panel, 2018–2024.
Data: nflverse schedules via sports_ds / nflreadpy; team-game grain.
Methods: shifted form features; constant vs logistic vs hist GBM.
Validation: season walk-forward.
Results: logistic mean log-loss beats constant; report per-season table.
Limits: no injuries/EPA roster model; team abbreviations raw.
Reproduce: sports-ds nfl-win-pipeline --seasons 2018-2024
```

---

## Bundled Resources

### references/
| File | Contents |
|---|---|
| `writeup_checklist.md` | completeness checklist |
| `templates.md` | short/long templates |

### scripts/
| File | Contents |
|---|---|
| `render_pipeline_report.py` | markdown report from pipeline JSON |

### related
- `model-card`, `experiment-log`, `anti-slop-analytics`, `calibration-check`

---

## Related Skills

| Need | Skill |
|---|---|
| Model card | `model-card` |
| Experiment log | `experiment-log` |
| Figures | `sports-visualization`, `anti-slop-analytics` |
| Calibration | `calibration-check` |
| Interpretation | `model-interpretation` |

---

## Quick Command Card

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win_pipeline.json
python skills/results-reporting/scripts/render_pipeline_report.py --json data/nfl_win_pipeline.json
```
