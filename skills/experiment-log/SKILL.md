---
name: experiment-log
description: >
  Record sports-modeling experiments with the hypothesis, data cut, validation
  charter, metrics, leakage status, decision, commands, and artifacts. Use for
  trials, model comparisons, and reproducible research history.
license: MIT
metadata:
  version: "0.7.0"
---

# Experiment Log

## Outcome

Create one immutable record per executed experiment. The log must let another
analyst reconstruct what was tried, compare it to its declared baseline, and
understand why it was kept, discarded, or queued for follow-up.

## Required inputs

- hypothesis and expected direction
- sport, grain, target, and decision time
- immutable data snapshot or query description
- feature-set reference with timing rules
- baseline and candidate configurations
- validation charter and primary metric
- random seeds and environment reference
- output artifacts and observed failures

## Schema

Each Markdown or JSON log must include:

```text
experiment_id
timestamp_utc
operator
hypothesis
sport
grain
target
prediction_timestamp_rule
data_sources
data_snapshot
data_window
feature_set_ref
baseline_refs
validation_charter_ref
model_family
config_ref
random_seeds
metrics_primary
metrics_secondary
leakage_audit_status
results_summary
decision
next_actions
artifacts
commands
notes
```

## Workflow

1. Create the log before fitting and freeze the hypothesis and primary metric.
2. Link immutable data, feature, validation, and configuration artifacts.
3. Record exact commands or notebook cell identifiers.
4. Execute the baseline and candidate under the same folds.
5. Store fold-level results, not only averages.
6. Record calibration, leakage, and failure checks where applicable.
7. Decide keep, discard, or follow-up using predeclared rules.
8. Append results; do not rewrite the original hypothesis after observing them.

## Decision rules

- **Keep:** improves the primary metric across meaningful held-out slices without
  violating timing, calibration, stability, or complexity constraints.
- **Discard:** fails the baseline, violates the charter, or adds complexity with
  no reliable held-out benefit.
- **Follow-up:** signal is plausible but uncertainty, data coverage, or a failed
  diagnostic prevents a decision.

## Hard constraints

- Never omit failed runs.
- Never change the primary metric after seeing results without a new log.
- Never compare models evaluated on different rows or folds without disclosure.
- Never overwrite an artifact referenced by a completed log.
- Never promote a model without a named baseline and timing audit.

## Helper

```bash
python <path-to-experiment-log>/scripts/new_experiment.py --slug home-form-logit --sport nfl
python <path-to-experiment-log>/scripts/new_experiment.py --slug elo-sensitivity --out-dir data/experiments
```

The helper creates a timestamped user-owned Markdown artifact and validates the slug.

## Resources

- `references/log_schema.md` — field definitions
- `references/decision_rules.md` — promotion logic
- `scripts/new_experiment.py` — portable log-stub writer
