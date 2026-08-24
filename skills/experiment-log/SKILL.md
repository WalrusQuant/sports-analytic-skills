---
name: experiment-log
description: >
  Record sports-modeling experiments in a reproducible log: hypothesis, data
  cut, validation charter, metrics, leakage status, decision, and artifacts.
  Use when running trials, comparing model versions, or preventing notebook
  amnesia — even if the user only says "log this run." Includes schema,
  decision rules, and a new-experiment stub script wired to sports_ds CLI paths
  for NFL/NBA/MLB.
version: "0.5.0"
license: MIT
metadata:
  version: "0.5.0"
---

# Experiment Log

## Overview

Ops skill for reproducible sports-modeling work.

**If it is not logged, it did not happen.**

Use before/after `sports-ds` pipeline runs so wins and losses both leave a trail.

---

## When to Use This Skill

Use when:

- Starting a training/evaluation run
- Comparing model variants (form vs Elo, win vs margin, NFL vs NBA)
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
- Sport + data window + target + T
- Validation reference
- Result summary
- Decision (`keep` / `discard` / `follow-up`)

Optional:

- Code commit hash / notebook path
- Config YAML / Elo params
- Random seeds
- Links to plots/metrics JSON

---

## Log Schema

```text
experiment_id: YYYYMMDD-<slug>-<nn>
timestamp_utc:
operator:
sport:
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
package_commands:
notes:
```

Full notes: `references/log_schema.md`  
Decision rules: `references/decision_rules.md`

---

## Workflow

1. **Create ID before the run** (not after seeing results).
2. **Write hypothesis in falsifiable form**
   - “NBA Elo logistic beats constant on 2024 walk-forward log-loss.”
3. **Attach charter + feature set refs** (`sports-ds feature-registry` names OK).
4. **Run once under locked config** via package CLI when possible.
5. **Log metrics exactly as specified by charter**
6. **Decision**
   - `keep` only if success threshold met
   - `discard` if failed honestly
   - `follow-up` if inconclusive with a specific next test
7. **Link artifacts** (metrics json, plots, commit)
8. **Update model card only on `keep` version bumps**

```bash
python skills/experiment-log/scripts/new_experiment.py --slug nba-elo-vs-const
python skills/experiment-log/scripts/new_experiment.py --slug mlb-margin-ridge --sport mlb --out-dir data/experiments
```

---

## Package command patterns to log

```bash
# NFL
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/exp_nfl_win.json
sports-ds nfl-margin-pipeline --seasons 2018-2024 --json-out data/exp_nfl_margin.json
sports-ds nfl-elo --seasons 2018-2024 --json-out data/exp_nfl_elo.json

# NBA / MLB (requires [multi])
sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1 --json-out data/exp_nba_win.json
sports-ds nba-elo --seasons 2023-2024 --min-train-seasons 1 --json-out data/exp_nba_elo.json
sports-ds mlb-margin-pipeline --seasons 2023-2024 --min-train-seasons 1 --json-out data/exp_mlb_margin.json
sports-ds mlb-elo --seasons 2023-2024 --min-train-seasons 1 --json-out data/exp_mlb_elo.json

# Trust checks
sports-ds leakage-audit --sport nba --seasons 2023-2024
sports-ds calibrate --sport mlb --seasons 2023-2024 --min-train-seasons 1
```

---

## Hard Constraints

1. Never invent metrics after the fact without labeling them post-hoc.
2. Never reuse an experiment ID for a different config.
3. Never log only winners.
4. Never claim reproducibility without data window + config + charter references.
5. Post-hoc metrics must be marked `post-hoc` and cannot silently drive the primary decision.
6. Sport and package command must be recorded for multi-sport work.

---

## Anti-Patterns

- Notebook folklore: “we tried this last week, pretty sure it worked”
- Winner’s log only
- Config amnesia
- Moving goalposts inside one ID
- Unlinked screenshots as evidence
- Logging NBA results under an NFL command path

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
experiment_id: 20260824-nba-elo-01
sport: nba
hypothesis: As-of Elo + home logistic beats constant train rate on 2024 walk-forward log-loss.
target: won
prediction_timestamp_rule: scheduled_start
data_window: 2023-2024
baseline_refs: [constant_train_rate]
validation_charter_ref: wf_season_min1
model_family: elo_logistic
metrics_primary: elo_logistic_log_loss vs constant_log_loss
leakage_audit_status: CLEAN
package_commands:
  - sports-ds nba-elo --seasons 2023-2024 --min-train-seasons 1 --json-out data/exp_nba_elo.json
decision: keep | discard | follow-up  # fill after run
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
python skills/experiment-log/scripts/new_experiment.py --slug nba-form-vs-elo
sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1 --json-out data/exp_nba_win.json
sports-ds nba-elo --seasons 2023-2024 --min-train-seasons 1 --json-out data/exp_nba_elo.json
python skills/results-reporting/scripts/render_pipeline_report.py --json data/exp_nba_elo.json
```
