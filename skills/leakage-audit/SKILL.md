---
name: leakage-audit
description: Audit sports modeling tables and workflows for target, temporal, join, preprocessing, and split leakage. Use before trusting backtests or reported predictive performance.
metadata:
  version: "0.12.0"
---

# Leakage Audit

## Outcome and stance

Assume leakage until the pipeline proves time-safe. Produce an adversarial,
evidence-backed verdict: `CLEAN`, `REVIEW REQUIRED`, or `NOT CLEAN`, with
contaminated fields, affected claims, required repairs, and retest conditions.
A strong metric is never evidence of cleanliness.

## When to Use This Skill

Use when:

- trusting a backtest or “good” metric for the first time;
- reviewing a feature table before modeling or after a suspiciously strong result;
- auditing target aliases, joins, shifts, preprocessing, or split design;
- the user says the model looks too good / results are unexpected.

Do **not** use this skill as a substitute for:

- designing legal features from scratch → `feature-rules`;
- designing folds and metrics → `validation-design`;
- first-pass panel EDA → `eda-sports`.

| Need | Go instead |
|---|---|
| Feature construction rules | `feature-rules` |
| Fold / metric charter | `validation-design` |
| Probability reliability after clean design | `calibration-check` |

## Lock the audit contract

Before inspecting correlations or metrics, write the target, row grain, exact
prediction decision time T, eligible population, source publication/revision
policy, and intended validation split. If T is ambiguous, the audit cannot pass.

Use [the audit checklist](references/audit_checklist.md) during every audit.
Consult [the leakage-pattern catalog](references/leakage_patterns.md) while
tracing failure modes and [the case studies](references/case_studies.md) when
performance or a join looks implausible.

## Audit sequence

1. Trace the target to its source and identify aliases, transformations, proxies,
   and duplicated labels.
2. Inventory every candidate feature, raw source, event/publication/revision time,
   and availability at T.
3. Inspect temporal transforms for stable sort and shift-before-roll/expand.
4. Trace opponent, roster, injury, rating, weather, price, and schedule joins.
5. Verify preprocessing, selection, encoding, and tuning fit only on training rows.
6. Verify validation moves forward in time and related rows remain together.
7. Run automated matrix heuristics, then manually investigate every finding.
8. Reproduce suspicious rows and performance jumps from raw inputs.
9. Issue the verdict and block unsupported claims until repair and rerun.

## Leakage catalog

| Pattern | Example | Evidence to inspect | Repair |
|---|---|---|---|
| Target alias | `won`, margin sign, final rank | lineage and exact/near correlation | remove from inputs |
| Same-event contamination | current score, EPA, box totals | source/event timestamps | target-only or redefine T |
| Unshifted history | current result in rolling mean | transform order and boundary rows | shift, then aggregate |
| Season bleed | final season average on week 2 | snapshot/publication policy | expanding prior value |
| Opponent contamination | opponent total includes matchup | join trace and paired rows | join safe opponent priors |
| Revision leakage | corrected stat used historically | publication/revision timestamps | reconstruct as-of vintage |
| Random row split | future games in train | fold date ranges | forward-only split |
| Group leakage | two game perspectives split apart | game/entity membership | group related rows |
| Preprocessing leak | scaler/encoder fit globally | fitted-object lineage | fit in training fold |
| Tuning leak | final fold drives hyperparameters | experiment history | nested tuning/untouched holdout |
| Duplicate leakage | same event or player appears in both | hashes and keys | deduplicate/group before split |

## Manual review

### Target and time

- Is the target post-T by definition, and are canceled/tied/incomplete events handled?
- Are prediction timestamps stored or reconstructable rather than assumed?
- Which provider fields are revised, and which historical vintage is used?
- Could a feature name be harmless while its source table is post-event?

### Transformations

```python
ordered = df.sort_values(["team", "event_time", "game_id"])
expected = ordered.groupby("team")["won"].transform(
    lambda s: s.shift(1).expanding(min_periods=1).mean()
)
assert expected.equals(ordered["pre_win_pct"])
```

Check sort tie-breaks, reset boundaries, offseason carryover, minimum periods,
and whether the first entity event has an unexplained empirical prior. A future
perturbation test should prove that changing later outcomes cannot alter earlier
features.

### Joins

For every join, document left/right grain, keys, expected cardinality,
publication-time predicate, unmatched rate, duplicate rate, and fields retained.
An as-of join must be backward-looking and satisfy `right_published_at <= T`.
Display-name joins and silent many-to-many expansion are audit failures until
resolved. Opponent features must equal the opponent's own pre-event row.

### Splits and preprocessing

For every fold prove `train max time < test min time`, allowing only the declared
gap/embargo. Keep paired team-game rows, repeated observations from the same
event, and other dependency groups together when the estimand requires it.
Imputers, scalers, encoders, selectors, target encoders, PCA, early stopping,
and hyperparameter search must see training data only.

### Too-good triggers

Near-perfect accuracy, implausibly low log-loss/error, a dramatic single-feature
jump, train/test equality, or a result far beyond domain baselines triggers a
stop. Recheck target aliases, current-event fields, shifts, opponent joins,
duplicates, global preprocessing, and test-fold tuning before discussing merit.

## Automated helpers

The audit helper reads a user-owned CSV, Parquet, JSON, JSONL, or NDJSON table,
requires `pandas`, validates named columns, and runs name, exact-target,
duplicate, and near-perfect-correlation heuristics.

```bash
python /path/to/leakage-audit/scripts/audit_pregame_features.py \
  --input modeling_table.csv --target won \
  --features pre_win_rate,rest_diff,rating_diff \
  --entity-col team --time-col event_time --out leakage.json

python /path/to/leakage-audit/scripts/write_audit_stub.py \
  --out data/leakage_audit.md
```

Use `--banned` to provide exact forbidden names for the task. The first-event
null-rate check is always `REVIEW`, not `PASS`, because legitimate priors can
populate first events. Duplicate rows and near-perfect correlations are also
`REVIEW`: they are suspicious, not proof by themselves. A direct forbidden or
target-identical feature returns `NOT CLEAN` and status 2. Otherwise the helper
returns `REVIEW REQUIRED` and status 1: heuristics alone never return `CLEAN`.
Only a completed manual audit of lineage, transforms, joins, splits, and
fold-local preprocessing can issue the `CLEAN` verdict.

### Exit codes (not crashes)

| Exit | Verdict | Agent action |
|---|---|---|
| 1 | `REVIEW REQUIRED` | **Continue.** Read the JSON. Complete the manual audit. Do not treat this as a hard failure. |
| 2 | `NOT CLEAN` | **Stop** predictive claims until repaired and retested. |
| 0 | unused | Heuristics never auto-CLEAN. |

Stderr also prints `exit=1 REVIEW REQUIRED...` or `exit=2 NOT CLEAN...` so a
cold agent does not mistake a review signal for a broken script.

Automated checks cannot prove source availability, transform correctness, join
direction, or fold scope. They supplement—not replace—lineage and code review.

## Diagnosis examples

**Rolling form without a shift:** manually recomputation shows row i contains
its own result. Mark `NOT CLEAN`, rebuild with `shift(1)`, regenerate all
downstream artifacts, and rerun validation.

**Final-season efficiency on early games:** the value is constant within season
and reflects later games. Replace with an expanding as-of statistic from prior
events; do not merely drop the first weeks.

**Legitimate first-event prior:** first rows have non-null ratings, but lineage
shows a fixed preseason rating published before T. Keep `REVIEW REQUIRED` until
the initialization and timestamp are documented, then pass that item.

**Random K-fold with clean features:** feature checks pass but future seasons
enter training. The pipeline is still `NOT CLEAN`; redesign folds and rerun all
reported metrics.

## Verdict rules

| Verdict | Meaning |
|---|---|
| `CLEAN` | complete inventory reviewed; no unresolved violations or review items |
| `REVIEW REQUIRED` | no proven contamination, but evidence or availability is incomplete |
| `NOT CLEAN` | at least one feature, join, transform, split, or tuning path uses forbidden information |

Uncertainty is not `CLEAN`. A fixed matrix must be regenerated and reevaluated;
deleting a suspicious column after scoring does not rescue prior metrics.

## Audit report template

```text
Leakage audit
Sport / question / target / grain:
Decision time T and publication policy:
Data snapshot and feature count:
Validation and grouping rule:
Automated helper result / exit status:
Lineage and transform evidence reviewed:
Findings:
  1. [PASS | REVIEW | FAIL] item, evidence, affected scope
Contaminated fields/artifacts:
Required repairs and retests:
Remaining uncertainty:
Verdict: CLEAN | REVIEW REQUIRED | NOT CLEAN
Auditor / date:
```

## Integrity and resource routing

1. Prefer a false review to a false clean; never infer cleanliness from metrics.
2. Timeline sort in the audit must match construction exactly.
3. Do not repair leakage by dropping a bad test period or redefining success.
4. `NOT CLEAN` blocks predictive claims until rebuilt and retested.
5. Use `references/audit_checklist.md` for completion,
   `references/leakage_patterns.md` for taxonomy, and
   `references/case_studies.md` for diagnosis.
6. Pair with `feature-rules` for remediation and `validation-design` for folds.
