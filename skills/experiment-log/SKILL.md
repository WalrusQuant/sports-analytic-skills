---
name: experiment-log
description: >
  Record sports-modeling experiments in a reproducible log: hypothesis, data
  cut, validation charter, metrics, leakage status, decision, and artifacts.
  Use when running trials, comparing model versions, or preventing notebook
  amnesia — even if the user only says "log this run." Includes schema,
  templates, and a new-experiment stub script.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# Experiment Log

## Overview

Ops skill for reproducible sports-modeling work.

**If it is not logged, it did not happen.**

---

## When to Use This Skill

Use when:

- Starting a training/evaluation run
- Comparing model variants
- After critique/audit decisions
- Before writing a model card version bump
- Any time an agent is about to overwrite results in a notebook cell and move on

Do **not** use when:

- Pure discussion with no run
- Designing the first validation charter only → `validation-design`

---

## Required Inputs

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

---

## Log Schema

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
regime_slice_metrics:
leakage_audit_status:
results_summary:
decision: keep | discard | follow-up
next_actions:
artifacts:
notes:
```

Full notes: `references/log_schema.md`

---

## Workflow

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
7. **Link artifacts** (metrics json, plots, commit)
8. **Update model card only on `keep` version bumps**

```bash
python skills/experiment-log/scripts/new_experiment.py --slug homewin-rest
python skills/experiment-log/scripts/new_experiment.py --slug elo-vs-form --out-dir data/experiments
```

---

## Hard Constraints

1. Never invent metrics after the fact without labeling them post-hoc.
2. Never reuse an experiment ID for a different config.
3. Never log only winners.
4. Never claim reproducibility without data window + config + charter references.
5. Post-hoc metrics must be marked `post-hoc` and cannot silently drive the primary decision.

---

## Anti-Patterns

- Notebook folklore: “we tried this last week, pretty sure it worked”
- Winner’s log only
- Config amnesia
- Moving goalposts inside one ID
- Unlinked screenshots as evidence

---

## Output Contract

Done means:

- [ ] Experiment ID assigned
- [ ] Hypothesis recorded before/at run start
- [ ] Charter/feature/baseline refs present
- [ ] Primary metrics logged
- [ ] Decision recorded with reason
- [ ] Artifacts linked or explicitly absent
- [ ] Follow-up (if any) is a single concrete next test

---

## Worked Example

```text
experiment_id: 20260824-homewin-rest-01
hypothesis: Pre-event rest differential improves log-loss vs rating-only logistic.
target: won
prediction_timestamp_rule: scheduled_start
data_window: 2018-2024 seasons
baseline_refs: [constant_train_rate, rating_logit_v2]
validation_charter_ref: wf_season_v1
model_family: logistic_rating_plus_rest
metrics_primary: log_loss=0.601 (vs 0.608 rating_logit_v2)
leakage_audit_status: clean
decision: keep
next_actions: freeze as candidate for model-card home_win_logit_v3
```

---

## Bundled Resources

### references/
- `log_schema.md`
- `decision_rules.md`

### scripts/
- `new_experiment.py`

---

## Related Skills

- `validation-design`
- `baseline-models`
- `leakage-audit`
- `model-card`
- `results-reporting`
- `sports-modeling-doctrine`

---

## Quick Command Card

```bash
python skills/experiment-log/scripts/new_experiment.py --slug nfl-win-form
```
