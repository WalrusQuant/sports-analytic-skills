---
name: leakage-audit
description: >
  Adversarial audit of sports modeling pipelines for look-ahead and target
  leakage. Use when reviewing features, joins, labels, splits, or any backtest
  that looks too good — even if the user only says "why is this so accurate"
  or "check for leaks." Covers pre-game legality, same-game contamination,
  season-aggregate bleed, split mistakes, opponent-join bugs, and automated
  sports_ds feature checks with a written CLEAN / NOT CLEAN verdict.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# Leakage Audit (Sports)

## Overview

Assume leakage until the pipeline proves time-safe.

This skill is an **adversarial review** of features, labels, joins, and splits
for sports predictive work. Output is a written audit with pass/fail items,
contaminated fields, required fixes, and a final verdict:

`CLEAN` | `NOT CLEAN`

A strong metric is never evidence of cleanliness.

---

## When to Use This Skill

Use when:

- Any feature matrix before claiming predictive performance
- Backtests that look suspiciously strong
- Reviewing joins across schedule, box score, injury, tracking, or lineup tables
- After `feature-rules` as a second pass
- Before publishing model results
- User says “why so accurate?” or “check for leaks”

Do **not** use as a substitute for:

| Need | Go to |
|---|---|
| Building legal features from scratch | `feature-rules` |
| Designing folds | `validation-design` |
| First EDA | `eda-sports` |

---

## Installation

```bash
pip install -e .
```

---

## Audit Workflow

Work in order. Do not skip to metrics.

1. **Lock decision time T** (kickoff, lineup lock, pitch release, …).
2. **Lock target** and grain (game, team-game, player-game, …).
3. **Inventory every feature** and when it becomes knowable.
4. **Inspect transforms** for missing `shift(1)` / as-of joins.
5. **Inspect opponent joins** — current-game contamination.
6. **Inspect splits** — future seasons/weeks in train; scaler fit scope.
7. **Run automated checks** on the matrix when possible.
8. **Write the verdict** with required repairs.

If T is ambiguous, stop and define T before continuing.

---

## Sports Leakage Catalog

| Pattern | Example | Fix |
|---|---|---|
| Same-game outcome as feature | `points_for`, `won`, current EPA | drop / target only |
| No shift on rolling form | `rolling(5).mean()` includes current game | `.shift(1)` then roll |
| Final-season stats on early weeks | season EPA average on week 1 | expanding as-of only |
| Opponent totals include current game | opp PF includes this matchup | opp pre-game only |
| Injury/participation without timestamp | inactive known post-game | timestamped source or drop |
| Random K-fold on games | future into train | season/week walk-forward |
| Target encoding on full data | mean win% by team all seasons | fit inside train fold only |
| Post-game join keys | final box merged to pre-game rows | as-of merge on time |
| Scaler fit on train+test | StandardScaler before split | fit on train only |
| Playoff labels mixed silently | different process, same model | flag or segment |

See `references/leakage_patterns.md` and `references/case_studies.md`.

---

## Automated Audit (`sports_ds` NFL features)

```bash
python skills/leakage-audit/scripts/audit_pregame_features.py --seasons 2023-2024
python skills/leakage-audit/scripts/audit_pregame_features.py --seasons 2018-2024 --out data/leakage_audit.json
```

Checks:

- banned outcome columns not in `FEATURE_COLS`
- first team game has NA pre-game form
- `pre_win_pct` not identical to current `won`
- required feature columns present

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

Also run:

```bash
python skills/predictive-modeling/scripts/leakage_smoke.py
python skills/feature-rules/scripts/legality_report.py --seasons 2023-2024
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
- [ ] Team-game double rows understood
- [ ] Opponent features merged as pre-game only
- [ ] No accidental use of both teams’ current scores

### D. Splits
- [ ] Train max time < test min time
- [ ] No scaler/encoder fit on full dataset before split
- [ ] Hyperparams tuned only inside train

### E. “Too good” triggers
If walk-forward log-loss is near-perfect or accuracy is absurd:
- [ ] Re-check same-game fields
- [ ] Re-check shift
- [ ] Re-check opponent merge
- [ ] Re-check test rows not in train feature fits

Printable copy: `references/audit_checklist.md`

---

## Worked Example (NFL pre-game win model)

**Legal**
- `is_home`
- shifted prior win % differential
- shifted rolling point-diff differential

**Illegal**
- current `points_for`
- current `won`
- final 2024 team EPA used in week 1 2024

Package path with legal form features:

`src/sports_ds/features/team_form.py` (`shift(1)` before expanding/rolling)

```bash
python skills/leakage-audit/scripts/audit_pregame_features.py --seasons 2023-2024
# expect verdict CLEAN for the stock pipeline features
```

---

## Audit Report Template

```text
Leakage audit
Target:
Grain:
Decision time T:\nFeature count:
Splits:

Findings:
1. [FAIL/PASS] …
2. [FAIL/PASS] …

Contaminated fields:
Required fixes:
Automated script results:
Verdict: CLEAN / NOT CLEAN
Auditor:
Date:
```

```bash
python skills/leakage-audit/scripts/write_audit_stub.py --out data/leakage_audit_report.md
```

---

## Hard Constraints

1. A strong metric is not evidence of cleanliness.
2. If legality is uncertain, mark **FAIL** until proven.
3. Do not “fix” leakage by dropping the ugly test season.
4. Document every exception (e.g. live in-game T).
5. `NOT CLEAN` blocks shipping claims until repaired.

---

## Integrity Rules

- Adversarial stance: try to break the pipeline.
- Prefer false FAIL over false CLEAN.
- Pair with `validation-design` — clean features + bad splits still leak.

---

## Bundled Resources

### references/
| File | Contents |
|---|---|
| `leakage_patterns.md` | extended pattern list |
| `audit_checklist.md` | printable checklist |
| `case_studies.md` | common sports leak stories |

### scripts/
| File | Contents |
|---|---|
| `audit_pregame_features.py` | automated sports_ds feature audit |
| `write_audit_stub.py` | blank audit report markdown |

### package code
- `src/sports_ds/features/team_form.py`
- `src/sports_ds/pipelines/nfl_win_model.py`

---

## Related Skills

| Need | Skill |
|---|---|
| Build features | `feature-rules` |
| Validation design | `validation-design` |
| Model run | `baseline-models` / `predictive-modeling` / `statistical-modeling` |
| Report | `results-reporting` |

---

## Quick Command Card

```bash
python skills/leakage-audit/scripts/audit_pregame_features.py --seasons 2023-2024
python skills/predictive-modeling/scripts/leakage_smoke.py
python skills/feature-rules/scripts/legality_report.py --seasons 2023-2024
python skills/leakage-audit/scripts/write_audit_stub.py --out data/leakage_audit_report.md
```
