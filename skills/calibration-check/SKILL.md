---
name: calibration-check
description: >
  Measure whether sports-model probabilities mean what they say. Use when
  evaluating probability quality, reliability curves, Brier score, expected
  calibration error, segment calibration, sharpness, or recalibration for
  win/event models — even if the user only asks "how confident is this" or
  "do these percentages make sense." Includes runnable walk-forward calibration
  reports on sports_ds outputs and a clear verdict scale.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# Calibration Check (Sports)

## Overview

A model can rank teams well and still be miscalibrated. If the model says 30%,
about 30% of those cases should hit.

This skill measures probability reliability for sports models and produces a
verdict an agent can act on.

Discrimination metrics (AUC, accuracy) do **not** replace calibration.

---

## When to Use This Skill

Use when:

- Model outputs win/event probabilities
- User asks how confident / how reliable the probs are
- After walk-forward evaluation of a probability model
- Before writing results that quote probability levels
- Comparing raw vs recalibrated probabilities

Do **not** use when:

- Pure ranking tasks with no probabilistic interpretation
- Hard labels only with no probability outputs
- Designing splits from scratch → `validation-design`
- Feature legality review → `leakage-audit`

---

## Installation

```bash
pip install -e .
```

---

## What to Measure

1. **Reliability / calibration curve** — bin predicted prob vs observed rate
2. **Expected Calibration Error (ECE)**
3. **Brier score** (+ reliability/resolution decomposition when useful)
4. **Log-loss** — discrimination + calibration together; not a substitute for ECE
5. **Segment calibration** — by season, home/away, probability tail
6. **Sharpness** — are probs informative, not all ~0.5?

Definitions: `references/calibration_metrics.md`

---

## Workflow

1. Confirm predictions come from time-safe / walk-forward folds.
2. Validate probabilities in (0, 1) with no NaNs.
3. Pre-declare binning (fixed-width or quantile).
4. Compute curve, ECE, Brier, log-loss.
5. Slice by season and by probability tails.
6. Issue a verdict (table below).
7. If recalibrating, only with nested/train-proper methods — never fit isotonic on the final test fold and call it validated.
8. Write the calibration report.

---

## Verdict Scale

| Verdict | Meaning |
|---|---|
| `well-calibrated` | Reliability acceptable for quoting probabilities |
| `usable-with-caveats` | Some miscalibration; disclose and/or recalibrate properly |
| `poorly-calibrated` | Probability numbers not trustworthy as probabilities |
| `invalid-eval` | Leakage/split issues block judgment |

Heuristic defaults used by the script (not laws):

- ECE ≤ 0.03 and adequate n → often `well-calibrated`
- ECE ≤ 0.07 → `usable-with-caveats`
- else → `poorly-calibrated`
- tiny n → caveats regardless

---

## Run on sports_ds NFL pipeline predictions

### Preferred script

```bash
python skills/calibration-check/scripts/calibration_report.py \
  --seasons 2018-2024 \
  --out data/calibration_report.json
```

Walk-forward logistic probs on sports_ds form features → Brier, log-loss, ECE, bin table, per-season rows, verdict.

### Python API

```python
import numpy as np
import sys
from pathlib import Path
sys.path.append(str(Path("skills/calibration-check/scripts").resolve()))
from calibration_report import (
    calibration_table,
    expected_calibration_error,
    brier_score,
    log_loss,
)

y = np.array([0, 1, 1, 0, 1], dtype=float)
p = np.array([0.2, 0.7, 0.8, 0.4, 0.6], dtype=float)
print(calibration_table(y, p, n_bins=5))
print(expected_calibration_error(y, p), brier_score(y, p), log_loss(y, p))
```

### Segment script

```bash
python skills/calibration-check/scripts/segment_calibration.py --seasons 2018-2024
```

---

## Binning Guidance

| Strategy | Use when |
|---|---|
| Equal-width (10 bins 0–1) | default sports win probs |
| Quantile bins | probs clump in a narrow range |
| Tail focus (0–0.2, 0.8–1.0) | decisions live in extremes |

Always report **bin counts**. Empty bins are not evidence.

See `references/binning.md`.

---

## Recalibration Rules

**Allowed**
- Platt scaling / isotonic fit **inside training folds only**, applied to test fold
- Nested walk-forward recalibration

**Not allowed**
- Fit isotonic on final test labels and call it validated
- Hand-edit probabilities after seeing outcomes

After recalibration, re-report ECE/Brier on true forward folds.

---

## Hard Constraints

1. Never evaluate calibration on training rows used to fit the same model without nested disclosure.
2. Never present raw scores as probabilities without checking calibration.
3. Never hide segment failures behind a pooled “looks fine.”
4. If sample per bin is tiny, say so — widen bins or reduce claim strength.
5. Accuracy is not calibration.

---

## Anti-Patterns

- “56% correct, so calibrated”
- One reliability plot with no sample sizes
- Holdout isotonic theater
- Average prob ≈ base rate therefore calibrated (necessary, not sufficient)
- Ignoring 0.05 and 0.95 tails

---

## Reporting Template

```text
Calibration report
Model:
Eval: walk-forward seasons …
n:
Brier:
ECE (bins=…):
Log-loss:
Notes by season:
Tail behavior:
Verdict: well-calibrated | usable-with-caveats | poorly-calibrated | invalid-eval
Actions:
```

---

## Worked Example

**Model:** pre-game team win probabilities from logistic form features  
**Design:** season walk-forward, 10 equal-width bins  
**Finding:** predictions near 0.70 hit only ~0.60 over several seasons; tails overconfident  
**Verdict:** `poorly-calibrated` for strong confidence language  
**Actions:** nested recalibration experiment; until then quote ranks more carefully than exact percents

```bash
python skills/calibration-check/scripts/calibration_report.py --seasons 2018-2024
```

---

## Bundled Resources

### references/
| File | Contents |
|---|---|
| `calibration_metrics.md` | ECE/Brier/log-loss definitions |
| `binning.md` | bin strategy notes |
| `recalibration.md` | allowed recalibration patterns |

### scripts/
| File | Contents |
|---|---|
| `calibration_report.py` | walk-forward calibration JSON |
| `segment_calibration.py` | home/away and tail slices |

### package code
- `src/sports_ds/models/baselines.py`
- `src/sports_ds/pipelines/nfl_win_model.py`

---

## Related Skills

| Need | Skill |
|---|---|
| Validation design | `validation-design` |
| Predictive models | `predictive-modeling` |
| Statistical models | `statistical-modeling` |
| Results writeup | `results-reporting` |
| Model card | `model-card` |

---

## Quick Command Card

```bash
python skills/calibration-check/scripts/calibration_report.py --seasons 2018-2024
python skills/calibration-check/scripts/segment_calibration.py --seasons 2018-2024
```
