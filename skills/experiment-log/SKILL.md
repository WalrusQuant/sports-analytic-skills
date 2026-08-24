---
name: experiment-log
description: >
  Record sports-modeling experiments in a reproducible log: hypothesis,
  data cut, validation charter, results, and decision. Use when running
  trials, comparing model versions, or preventing notebook amnesia.
version: "0.1.0"
license: MIT
---

# Experiment Log

Ops skill for reproducible sports-modeling work. If it is not logged, it
did not happen.

## When to use

- Starting a training/evaluation run
- Comparing model variants
- After critique/audit decisions
- Before writing a model card version bump
- Any time an agent is about to overwrite results in a notebook cell and move on

## When not to use

- Pure discussion with no run
- Final public essay writing → `edge-writeup` / `ethics`
- Designing the first validation charter only → `validation-design`

## Required inputs

Minimum:

- Experiment ID (or generate one)
- Hypothesis / change being tested
- Data window + target + T
- Validation reference
- Result summary
- Decision (`keep` / `discard` / `follow-up`)

Optional:

- Code commit hash / notebook path
- Config YAML
- Random seeds
- Links to plots/metrics files

## Log schema

Use one record per experiment:

```text
experiment_id: YYYYMMDD-<slug>-<nn>
timestamp_utc:
operator:
hypothesis:
claim_level_sought:
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
regime_slice_metrics:
leakage_audit_status:
results_summary:
decision: keep | discard | follow-up
next_actions:
artifacts:
notes:
```

## Procedure

1. **Create ID before the run** (not after seeing results).
2. **Write hypothesis in falsifiable form**
   - “Adding rest-differential improves walk-forward log-loss vs baseline B.”
3. **Attach charter + feature set refs**
4. **Run once under locked config**
5. **Log metrics exactly as specified by charter**
6. **Decision**
   - `keep` only if success threshold met
   - `discard` if failed honestly
   - `follow-up` if inconclusive with a specific next test
7. **Link artifacts**
   - metrics json, plots, model blob path, commit
8. **Update model card only on `keep` version bumps**

## Hard constraints

- Never invent metrics after the fact without labeling them post-hoc
- Never reuse an experiment ID for a different config
- Never log only winners
- Never claim reproducibility without data window + config + charter references
- Post-hoc metrics must be marked `post-hoc` and cannot drive the primary decision silently

## Anti-patterns

- **Notebook folklore:** “we tried this last week, pretty sure it worked”
- **Winner’s log only**
- **Config amnesia**
- **Moving goalposts inside one ID**
- **Unlinked screenshots as evidence**

## Output contract

Done means:

- [ ] Experiment ID assigned
- [ ] Hypothesis recorded before/at run start
- [ ] Charter/feature/baseline refs present
- [ ] Primary metrics logged
- [ ] Decision recorded with reason
- [ ] Artifacts linked or explicitly absent
- [ ] Follow-up (if any) is a single concrete next test

## Handoffs

- `validation-design` — if charter missing
- `baseline-models` — if baseline refs missing
- `leakage-audit` — if audit status unknown on a keep candidate
- `model-card` — on kept version
- `doctrine` — claim level changes from cumulative evidence
- **Stop** after discard unless a new hypothesis exists

## Worked example

```text
experiment_id: 20260824-homewin-rest-01
hypothesis: Pre-event rest differential improves log-loss vs rating-only logistic.
claim_level_sought: paper
target: home_win
prediction_timestamp_rule: scheduled_start
data_window: 2018-2024 seasons
baseline_refs: [season_home_rate, rating_logit_v2]
validation_charter_ref: wf_season_v1
model_family: logistic_rating_plus_rest
metrics_primary: log_loss=0.601 (vs 0.608 rating_logit_v2)
leakage_audit_status: clean
decision: keep
next_actions: freeze as candidate for model-card home_win_logit_v3
```

## References

- `skills/validation-design`
- `skills/model-card`
- `skills/doctrine`
- `skills/baseline-models`
