---
name: leakage-audit
description: Audit sports modeling tables and workflows for target, temporal, join, preprocessing, and split leakage. Use before trusting backtests or reported predictive performance.
---

# Leakage Audit

Start by writing the target, row grain, prediction decision time, and data publication policy. Judge every column and transformation relative to that contract.

## Audit sequence

1. Trace the target backward to its source and rule out aliases or derived copies in features.
2. Check raw availability timestamps, revisions, postponed events, and as-of joins.
3. Inspect rolling features for an outcome shift before aggregation.
4. Verify opponent, roster, injury, odds, and rating joins cannot see later updates.
5. Confirm preprocessing and feature selection are fitted separately inside training folds.
6. Confirm validation moves forward in time and keeps related rows together where appropriate.
7. Review suspiciously strong correlations, duplicates, and abrupt performance jumps.
8. Issue a written `CLEAN`, `REVIEW REQUIRED`, or `NOT CLEAN` verdict with evidence and required fixes.

Read [references/audit_checklist.md](references/audit_checklist.md) during the audit, [references/leakage_patterns.md](references/leakage_patterns.md) for failure modes, and [references/case_studies.md](references/case_studies.md) when a result looks implausibly strong.

## Bundled helpers

The audit helper accepts a user-owned CSV, Parquet, JSON, JSONL, or NDJSON table and requires pandas. It validates all named columns and runs name, exact-target, duplicate, and near-perfect-correlation heuristics.

```bash
python /path/to/leakage-audit/scripts/audit_pregame_features.py \
  --input modeling_table.csv --target won \
  --features pre_win_rate,rest_diff,rating_diff \
  --entity-col team --time-col event_time --out leakage.json

python /path/to/leakage-audit/scripts/write_audit_stub.py --out leakage_audit.md
```

The first-event null-rate finding is always `REVIEW`, not `PASS`: legitimate
priors can populate first events, so the rate needs human interpretation. When
there are no hard failures but this finding is present, the helper returns
`REVIEW REQUIRED` and exits with status 1. Hard failures return `NOT CLEAN` and
status 2; only a run with no failures or review findings returns `CLEAN` and
status 0. Automated checks cannot prove point-in-time availability, so pair them
with source and transformation review. Replace `/path/to/leakage-audit` with the
installed skill path.
