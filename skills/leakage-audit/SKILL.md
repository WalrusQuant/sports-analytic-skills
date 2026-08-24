---
name: leakage-audit
description: >
  Audit sports modeling pipelines for look-ahead and target leakage. Use when
  reviewing features, joins, labels, splits, or any backtest that looks too
  good. Covers pre-game legality, same-game contamination, season-aggregate
  bleed, split mistakes, and sports_ds feature checks with a runnable auditor.
version: "0.3.0"
license: MIT
metadata:
  version: "0.3.0"
---

# Leakage Audit (Sports)

## Overview

Assume leakage until the pipeline proves time-safe. This skill is an adversarial
review of features, labels, joins, and splits for sports predictive work.

Output: a written audit with pass/fail items, contaminated fields, and required fixes.

## When to Use This Skill

- Any feature matrix before claiming predictive performance
- Backtests that look suspiciously strong
- Reviewing joins across schedule, box score, injury, tracking, or lineup tables
- After `feature-rules` as a second pass
- Before publishing model results

---

## Installation

```bash
pip install -e .
```

---

## Audit Workflow

1. **Lock decision time T** (e.g., scheduled kickoff, lineup lock, pitch release).
2. **Lock target** (win, margin, player stat, etc.) and grain.
3. **Inventory every feature** and when it becomes knowable.
4. **Inspect transforms** for missing `shift(1)` / as-of joins.
5. **Inspect splits** for future seasons/weeks in train.
6. **Run automated checks** on the matrix when possible.
7. **Write the verdict** with required repairs.

Do not skip to metrics.

---

## Sports Leakage Catalog

| Pattern | Example | Fix |
|---|---|---|
| Same-game outcome as feature | `points_for`, `won`, current EPA | drop / use only as target |
| No shift on rolling form | `rolling(5).mean()` includes current game | `.shift(1)` then roll |
| Final-season stats on early weeks | season EPA average on week 1 | expanding as-of only |
| Opponent season totals include current game | opp PF includes this matchup | compute opp pre-game only |
| Injury/participation without timestamp | “inactive” known post-game | timestamped source or drop |
| Random K-fold on games | shuffles future into train | season/week walk-forward |
| Target encoding fit on full data | mean win rate by team on all seasons | fit inside train fold only |
| Post-game join keys | merging final box to pre-game rows | as-of merge on time |

---

## Automated Audit (`sports_ds` NFL features)

```bash
python skills/leakage-audit/scripts/audit_pregame_features.py --seasons 2023-2024
```

What it checks:

- banned outcome columns not in model feature list
- first team game has NA pre-game form
- `pre_*` / rolling features are not identical to current `won`
- pipeline feature list from `sports_ds.pipelines.nfl_win_model.FEATURE_COLS`

Python:

```python
import sys
from pathlib import Path
sys.path.append(str(Path("skills/leakage-audit/scripts").resolve()))
from audit_pregame_features import audit_frame

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features

df = add_pregame_form_features(load_team_game_panel([2023, 2024]))
print(audit_frame(df))
```

---

## Manual Review Checklist

### A. Target and T

- [ ] Target definition written
- [ ] T written in plain language
- [ ] Labels cannot be known before T

### B. Feature legality

For each feature:

- [ ] Source table/time known
- [ ] Legal at T? yes/no
- [ ] If delayed, delay handled

### C. Panel construction

- [ ] Team-game double rows understood (home and away)
- [ ] Opponent features merged as pre-game only
- [ ] No accidental use of both teams’ current scores

### D. Splits

- [ ] Train max time < test min time
- [ ] No scaler/encoder fit on full dataset before split
- [ ] Hyperparams tuned only inside train

### E. “Too good” triggers

If walk-forward log-loss is near-perfect or accuracy is absurd for the sport:

- [ ] Re-check same-game fields
- [ ] Re-check shift
- [ ] Re-check opponent merge
- [ ] Re-check that test rows were not in train feature fits

---

## Worked Example (NFL pre-game win model)

Legal:

- `is_home`
- shifted prior win % differential
- shifted rolling point-diff differential

Illegal:

- current `points_for`
- current `won`
- final 2024 team EPA used in week 1 2024

Package path that implements legal form features:

`src/sports_ds/features/team_form.py` (`shift(1)` before expanding/rolling)

---

## Audit Report Template

```text
Leakage audit
Target: …
Grain: …
Decision time T: …
Feature count: …
Splits: …

Findings:
1. [FAIL/PASS] …
2. [FAIL/PASS] …

Contaminated fields: …
Required fixes: …
Verdict: CLEAN / NOT CLEAN
```

---

## Hard Constraints

1. A strong metric is not evidence of cleanliness.
2. If legality is uncertain, mark FAIL until proven.
3. Do not “fix” leakage by dropping the ugly test season.
4. Document every exception (e.g., live in-game T).

---

## Bundled Resources

### scripts/

- `audit_pregame_features.py` — automated checks for sports_ds pre-game features

### references/

- `leakage_patterns.md` — extended pattern list

### package code

- `src/sports_ds/features/team_form.py`
- `src/sports_ds/pipelines/nfl_win_model.py`

---

## Related skills

- Build features: `feature-rules`
- Validation design: `validation-design`
- Model run: `baseline-models` / `predictive-modeling` / `statistical-modeling`
