---
name: experiment-log
description: >
  Record sports-modeling experiments with the hypothesis, data cut, validation
  charter, metrics, leakage status, decision, commands, and artifacts. Use for
  trials, model comparisons, and reproducible research history.
license: MIT
metadata:
  version: "0.12.0"
---

# Experiment Log

## When to Use This Skill

Use when:

- starting a modeling experiment that should be comparable later;
- the user asks “what did we try?” or needs a decision history;
- promoting/rejecting candidates under a locked validation design;
- recording failures, deviations, and why a model was or was not shipped.

Do **not** use this skill as a substitute for:

- locking metrics and folds → `validation-design`;
- writing the public-facing results narrative → `results-reporting`;
- the durable model contract → `model-card`.

| Need | Go instead |
|---|---|
| Validation charter | `validation-design` |
| Results writeup | `results-reporting` |
| Model contract | `model-card` |

## Outcome

Create one immutable record per executed experiment so another analyst can
reconstruct what was tried, compare it with its declared baseline, audit its
validity, and understand why it was kept, discarded, or queued for follow-up.
Failed runs are evidence and belong in the history.

An experiment log is trial history. A validation charter defines evaluation; a
model card freezes a promoted model contract; a results report explains an
evaluation to readers.

Read [the log schema](references/log_schema.md) while creating or auditing a
record and [the decision rules](references/decision_rules.md) before assigning
the final decision.

## Create before execution

Record before fitting:

- unique ID, UTC timestamp, operator, falsifiable hypothesis, expected direction;
- sport, competition, row grain, target, population, and decision time T;
- immutable data snapshot/query and its source/retrieval metadata;
- feature-set reference with availability and transformation rules;
- baseline/candidate configuration, validation charter, and locked primary metric;
- code version, environment/lock reference, random seeds, and exact command;
- predeclared success, integrity, calibration, stability, and complexity limits.

Do not rewrite these fields after observing results. Corrections and deviations
are appended with timestamp, author, reason, and effect on validity.

## Schema

```text
experiment_id: YYYYMMDD-<slug>-<nn>
created_at_utc:
operator:
hypothesis / expected direction:
sport / competition / grain / target / eligible population:
prediction_timestamp_rule:
data_sources / immutable_snapshot / data_window:
feature_set_ref / baseline_refs:
validation_charter_ref / primary_metric / success_rule:
model_family / config_ref / code_version / environment_ref:
random_seeds / commands:
status: planned | running | completed | failed | invalidated
fold_metrics / metrics_primary / metrics_secondary:
calibration / slice / stability results:
leakage_audit_status / failures / deviations:
results_summary:
decision: keep | discard | follow-up | invalid
decision_reason / next_actions:
artifacts / checksums / notes:
```

## Workflow

1. Search existing logs, assign a new ID, and create the record before the run.
2. Freeze the falsifiable hypothesis, primary metric, baselines, and success rule.
3. Link immutable data, feature, validation, config, code, and environment artifacts.
4. Record exact noninteractive commands or notebook cell/version identifiers.
5. Execute baseline and candidate on identical eligible rows and folds.
6. Append fold-level metrics, runtime, warnings, and output artifact checksums.
7. Record calibration, leakage, slice, and failure diagnostics where applicable.
8. Mark deviations and invalid runs; never delete or convert them into successes.
9. Decide from the predeclared rule, then record one concrete next action if needed.
10. Promote to a model card only after `keep` and all integrity gates pass.

## Comparison discipline

Candidate comparisons are valid only when target, T, population, data snapshot,
rows, folds, metrics, and baseline definitions match. If they differ, log the
difference and do not attribute the metric change solely to the model.

Store per-fold results rather than averages only:

```text
fold | train_period | test_period | n | baseline_primary | candidate_primary |
gap | secondary_metrics | calibration | warnings
```

Include uncertainty or dispersion appropriate to the design. Never promote a
candidate because one favorable fold offsets repeated failures hidden by a mean.

## Decision rules

| Decision | Use when |
|---|---|
| `keep` | predeclared success met on locked evaluation and integrity gates pass |
| `discard` | honestly fails baseline/rule or adds unsupported complexity |
| `follow-up` | signal is plausible but one named uncertainty needs one concrete test |
| `invalid` | leakage, execution failure, charter violation, or incomparable rows prevents inference |

Post-hoc metrics must be labeled `post-hoc` and cannot silently drive the
primary decision. A changed metric, population, or hypothesis requires a new ID.

## Failure and deviation handling

Record nonzero exits, exceptions, timeouts, warnings, empty folds, missing
artifacts, convergence failures, seed instability, and manual intervention.
Include the last valid stage and whether partial outputs are trustworthy.

When leakage or a validation violation is found later, append an invalidation
entry to every affected experiment and downstream artifact. Do not overwrite
the original record or reuse its metrics after repair; the repaired run gets a
new experiment ID linked to the invalidated one.

## Anti-patterns

| Anti-pattern | Consequence | Correct behavior |
|---|---|---|
| winner-only logging | selection bias disappears from history | log all planned/executed runs |
| hypothesis written after score | retrospective story | freeze before fitting |
| reused experiment ID | configurations become ambiguous | new ID for every material change |
| mutable data path only | run cannot be reconstructed | snapshot/query + checksum/version |
| screenshots without raw metrics | evidence cannot be audited | link structured fold metrics |
| changed rows/folds undisclosed | comparison is confounded | common sample or explicit caveat |
| final metric replaced post-hoc | goalposts move | label exploratory; new experiment |
| failed run deleted | troubleshooting and selection history lost | status `failed` with evidence |

## Standalone helper

```bash
python /path/to/experiment-log/scripts/new_experiment.py \
  --slug home-form-logit --sport nfl
python /path/to/experiment-log/scripts/new_experiment.py \
  --slug elo-sensitivity --out-dir data/experiments
```

The helper creates a timestamped, user-owned Markdown artifact and validates
the slug. Creation is exclusive: concurrent invocations retry the sequence and
never overwrite or reuse an existing ID. The stub contains every field in the
required schema, but it is only a `planned` record; complete the pre-run fields
before execution and append results/deviations without rewriting the frozen
contract.

## Worked example

```text
experiment_id: 20260824-home-form-logit-01
hypothesis: Shifted 5-game form improves test log-loss over constant train rate.
sport / grain / target: nfl / team-game / won
prediction_timestamp_rule: scheduled kickoff
immutable_snapshot: snapshots/nfl_team_game_2019_2025.parquet (sha256: ...)
feature_set_ref: feature-cards/team-form-v3.md
validation_charter_ref: charters/season-wf-v2.md
primary_metric: log-loss
success_rule: beat baseline on mean and majority of outer folds; audit CLEAN
commands: [exact invocation]
status: completed
fold_metrics: artifacts/20260824-home-form-logit-01-folds.json
leakage_audit_status: CLEAN
decision: keep | discard | follow-up | invalid
decision_reason: fill after evaluation
```

## Review checklist and integrity rules

- ID existed before results; hypothesis is falsifiable.
- Data, code, config, feature, charter, environment, seeds, and commands resolve.
- Baseline/candidate share rows, folds, and metrics or differences are disclosed.
- Fold-level results and failed checks are present.
- Leakage status and decision follow the predeclared rule.
- Referenced artifacts are immutable and checksummed where practical.

Never omit failed runs, alter the primary metric silently, overwrite referenced
artifacts, or promote without a baseline and timing audit. Use `log_schema.md`
for required field semantics and `decision_rules.md` for promotion logic.
