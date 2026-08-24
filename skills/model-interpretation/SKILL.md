---
name: model-interpretation
description: >
  Interpret sports models without fooling yourself: coefficient/effect reads,
  error slices, largest misses, calibration context, and stability checks
  across seasons. Use after a walk-forward run when explaining why a model
  wins or fails — even if the user only says "why did it miss" or "what
  drives this." Includes slice scripts and package JSON handoffs for
  NFL/NBA/MLB.
version: "0.5.0"
license: MIT
metadata:
  version: "0.5.0"
---

# Model Interpretation (Sports)

## Overview

Explain model behavior after evaluation — not instead of evaluation.

Interpretation answers:

- what the model relies on
- where it fails
- whether failures are concentrated (home/away, season, probability tails)

It does **not** turn a losing walk-forward into a win.

---

## When to Use This Skill

Use when:

- After win/margin/Elo pipelines finish
- Debugging bad folds
- Writing results/model cards
- User asks “why” / “largest misses” / “where does it break”

Do **not** use when:

- No held-out predictions yet
- Leakage still open → `leakage-audit` first
- Pure presentation cleanup → `anti-slop-analytics`

---

## Installation\n
```bash
pip install -e .
pip install -e ".[multi]"   # NBA/MLB panels
```

---

## Workflow

1. Confirm the evaluation is walk-forward (not in-sample flex).
2. Collect predictions + actuals + keys (season, team, is_home, p_hat).
3. Global metrics first (already in pipeline JSON).
4. Slice errors by season / home-away / probability bins.
5. List largest misses with context (favorite blown out, etc.).
6. For linear models: read coefficients with scale caveats.
7. For trees: prefer slice stability over single importance bar chart.
8. Feed findings into `results-reporting` / `model-card`.

```bash
# produce artifacts
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win.json
sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1 --json-out data/nba_win.json

# slice helpers
python skills/model-interpretation/scripts/slice_errors.py --seasons 2018-2024
python skills/model-interpretation/scripts/largest_misses.py --seasons 2018-2024
```

Methods: `references/interpretation_methods.md`  
Slice guide: `references/slice_guide.md`

---

## Hard Constraints

1. Never interpret a model that failed leakage.
2. Never treat coefficient sign as causal without design.
3. Never hide slices where the model loses.
4. Probability tails need calibration context (`calibration-check`).
5. One season hero story is not generalization.

---

## Anti-Patterns

- Feature importance theater without metric lift
- Explaining noise as narrative
- Only showing best-case slices
- Confusing correlation of form features with “team quality truth”

---

## Output Contract

- [ ] Global metrics restated with baseline
- [ ] At least two slices reported
- [ ] Largest misses listed with context
- [ ] Limits of interpretation stated
- [ ] Next test named if follow-up needed

---

## Bundled Resources

### references/
- `interpretation_methods.md`
- `slice_guide.md`

### scripts/
- `slice_errors.py`
- `largest_misses.py`

---

## Related Skills

- `results-reporting`
- `calibration-check`
- `model-card`
- `predictive-modeling`
- `statistical-modeling`

---

## Quick Command Card

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win.json
python skills/model-interpretation/scripts/slice_errors.py --seasons 2018-2024
python skills/model-interpretation/scripts/largest_misses.py --seasons 2018-2024
sports-ds calibrate --sport nba --seasons 2023-2024 --min-train-seasons 1
```
