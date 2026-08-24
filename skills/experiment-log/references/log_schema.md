# Experiment Log Schema

```text
experiment_id: YYYYMMDD-<slug>-<nn>
timestamp_utc:
operator:
hypothesis:
target:
prediction_timestamp_rule:
data_sources:
data_window:
feature_set_ref:
baseline_refs:
validation_charter_ref:
model_family:
config_ref:
metrics_primary:
metrics_secondary:
leakage_audit_status:
results_summary:
decision: keep | discard | follow-up
next_actions:
artifacts:
notes:
```

Rules:

- Create ID before the run
- Hypothesis must be falsifiable
- Log losers as well as winners
- Post-hoc metrics must be labeled post-hoc
