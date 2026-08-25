# Experiment Log Schema

```text
experiment_id: YYYYMMDD-<slug>-<nn>
created_at_utc:
operator:
hypothesis:
expected_direction:
sport:
competition:
grain:
target:
eligible_population:
prediction_timestamp_rule:
data_sources:
immutable_snapshot:
data_window:
feature_set_ref:
baseline_refs:
validation_charter_ref:
primary_metric:
success_rule:
model_family:
config_ref:
code_version:
environment_ref:
random_seeds:
commands:
status: planned | running | completed | failed | invalidated
fold_metrics:
metrics_primary:
metrics_secondary:
calibration_results:
slice_results:
stability_results:
leakage_audit_status:
failures:
deviations:
results_summary:
decision: keep | discard | follow-up | invalid
decision_reason:
next_actions:
artifacts:
checksums:
notes:
```

Rules:

- Create ID before the run
- Create files exclusively; never overwrite or reuse an existing ID
- Hypothesis must be falsifiable
- Freeze primary metric, baseline, and success rule before execution
- Log losers as well as winners
- Post-hoc metrics must be labeled post-hoc
- Append timestamped corrections and deviations; do not rewrite frozen fields
