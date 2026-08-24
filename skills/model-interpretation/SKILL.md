---
name: model-interpretation
description: >
  Interpret sports models after fit: coefficient tables, odds ratios, feature
  effects, error slices by season/home/tails, largest misses, ablation checks,
  and limits under leakage-safe features. Use after fitting a sports model to
  explain behavior and failure modes — even if the user only asks "what is the
  model using" or "where does it fail." Includes walk-forward slice scripts.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# Model Interpretation (Sports)

## Overview

Explain what a sports model is doing and where it fails:

- **global** drivers (coefs / importances)
- **local** example games
- **segments** (season, home/away, probability tails)

Interpretation is **not causality**. It is structured description tied to validated performance.

---

## When to Use This Skill

Use when:

- After baseline / ML / statistical model fit
- Need driver explanations for a report
- Debugging segment failures (home dogs, early season, blowouts)
- Checking whether “important” features are just leakage
- User asks “what is it using?” or “where does it fail?”

Do **not** use when:

- Model not trained yet
- Features known leaked — fix with `leakage-audit` / `feature-rules` first

---

## Installation

```bash
pip install -e .\n```

---

## Techniques

| Technique | Good for | Caution |
|---|---|---|
| GLM coefficients / odds ratios | logistic/linear sports models | scale and collinearity |
| Tree importances | GBM/histGBM | unstable, not causal |
| Partial dependence / ALE-style | nonlinear effects | correlated features |
| Residual / error slices | finding broken segments | need enough n |
| Largest misses case study | intuition checks | anecdote risk |
| Ablation | feature group value | do walk-forward |

Details: `references/interpretation_methods.md`

---

## Workflow

1. Confirm features are time-safe.
2. **Global picture:** top drivers (coefs or importances).
3. **Local picture:** example games with large errors.
4. **Slice errors** by season, home/away, predicted-prob buckets.
5. Separate correlation from actionable explanation.
6. Document limits.
7. Hand off to `results-reporting`.

---

## Scripts

### Error slices on walk-forward logistic

```bash
python skills/model-interpretation/scripts/slice_errors.py \
  --seasons 2018-2024 \
  --out data/slice_errors.json
```

Reports log-loss/accuracy by season and home/away for the sports_ds logistic baseline.

### Coefficient / OR view

```bash
python skills/statistical-modeling/scripts/glm_diagnostics.py --seasons 2018-2023
```

### Largest misses

```bash
python skills/model-interpretation/scripts/largest_misses.py --seasons 2018-2024 --top 20
```

---

## Slice Checklist (Sports)

- [ ] By season
- [ ] Home vs away
- [ ] Early season vs late season (week buckets)
- [ ] Predicted probability tails (0–0.2, 0.8–1.0)
- [ ] Large favorite / large dog buckets if rating/prob available

Mark slices with tiny n as unstable.  
See `references/slice_guide.md`.

---

## Hard Constraints

1. Importance ≠ causality.
2. Don’t explain a leaked model as insight.
3. Slice metrics with enough n or mark unstable.
4. Keep interpretation tied to validation evidence.
5. No story-fitting after peeking at one weird game only.

---

## Anti-Patterns

- SHAP theater on a contaminated pipeline
- One importance bar chart as the whole story
- Ignoring systematic miss segments
- Causal language from observational sports data
- Explaining in-sample fit as generalization

---

## Reporting Template

```text
Interpretation
Model:
Global drivers:
Key slices:
Largest misses:
Ablation (if any):
Limits: correlational; time-safe features only; …
```

---

## Bundled Resources

### references/
| File | Contents |
|---|---|
| `interpretation_methods.md` | methods overview |
| `slice_guide.md` | segment checklist |

### scripts/
| File | Contents |
|---|---|
| `slice_errors.py` | walk-forward error slices |
| `largest_misses.py` | biggest probability misses |

### related package
- `src/sports_ds/models/baselines.py`
- `skills/statistical-modeling/scripts/glm_diagnostics.py`

---

## Related Skills

| Need | Skill |
|---|---|
| Reporting | `results-reporting` |
| Features | `feature-rules` |
| Leakage | `leakage-audit` |
| EDA | `eda-sports` |
| Calibration | `calibration-check` |

---

## Quick Command Card

```bash
python skills/model-interpretation/scripts/slice_errors.py --seasons 2018-2024
python skills/model-interpretation/scripts/largest_misses.py --seasons 2018-2024
python skills/statistical-modeling/scripts/glm_diagnostics.py --seasons 2018-2023
```
