---
name: model-card
description: >
  Write a durable sports model card covering identity, intended use, target,
  decision time, data, features, baselines, validation, results, limits,
  maintenance, and kill conditions. Use when freezing or sharing a model.
license: MIT
metadata:
  version: "0.12.0"
---

# Sports Model Card

## Outcome

Create a versioned operating contract tied to user-owned model, data, metrics,
feature, and validation artifacts. A model card describes an already evaluated
model: what it is for, how it was tested, where it fails, and when to retrain or
retire it.

A card is not a marketing page, experiment history, or substitute for evidence.
Use `experiment-log` for the sequence of trials and `results-reporting` for the
human-readable story of a particular evaluation.

## When to use this skill

Use it when:

- a model has stable held-out evidence worth keeping;
- promoting an accepted experiment into a named version;
- preparing a model for reuse, handoff, review, or publication;
- updating the documentation for a new immutable model version;
- the user asks to document, freeze, or share a sports model.

Do not create a polished card to imply maturity that the model has not earned.
If validation, a baseline, or decision-time legality is unknown, state that
explicitly and mark the model unapproved for operational use.

## Required evidence

- stable model name and version;
- owner, reviewers, creation date, and next review date;
- intended users, decisions, and prohibited uses;
- sport, competition, population, grain, target, and decision time;
- data provenance, window, filters, exclusions, and immutable snapshot;
- feature definitions and availability timing;
- named naive and strong simple baselines;
- validation design, fold boundaries, and metric definitions;
- aggregate and fold-level results on identical held-out populations;
- calibration, leakage, fairness, stability, and slice findings as applicable;
- serialized model, environment information, and reproduction instructions;
- monitoring, retraining, and retirement criteria.

Use `unknown`, `not tested`, or `not applicable` when truthful. Never fill a gap
with an inferred value or a generic promise.

## Required sections

1. Identity, ownership, status, and version
2. Intended use, users, decisions, and prohibited uses
3. Target, grain, prediction timestamp, horizon, and output semantics
4. Data sources, window, population, exclusions, and snapshot
5. Feature families, transformations, and time-safety rules
6. Baselines and candidate family
7. Validation design, fold construction, and metric definitions
8. Results with uncertainty, fold variation, slices, and calibration
9. Known limitations, failure modes, and misuse risks
10. Monitoring, retraining, review, and retirement rules
11. Artifact manifest, dependencies, and reproduction instructions
12. Approval history and linked experiments

For a fill-in structure, read
[`references/card_template.md`](references/card_template.md). Before defining
monitoring or retirement rules, read
[`references/kill_conditions.md`](references/kill_conditions.md) and adapt the
examples to the actual decision and metric.

## Workflow

1. Confirm that the candidate met the predeclared acceptance rule on held-out
   data. If not, document it as experimental or abandoned rather than approved.
2. Verify the model version and immutable artifact identifiers.
3. Copy factual fields from experiment, data, feature, leakage, calibration,
   and validation artifacts; do not reconstruct them from memory.
4. State intended use narrowly and list explicit prohibited uses.
5. Describe data coverage, exclusions, label construction, and populations not
   represented by evaluation.
6. Document each feature family and prove availability at decision time.
7. Present candidate and baselines on identical folds and rows.
8. Summarize the primary metric first, then uncertainty, calibration, stability,
   and error slices.
9. Convert known failure modes into checkable monitoring and kill conditions.
10. Record exact artifact paths and reproduction instructions supplied by the
    user or environment.
11. Have a second reviewer trace every quantitative and operational claim.
12. Freeze the version; future substantive changes create a new card.

## Status and freeze rules

| Event | Card action |
|---|---|
| First candidate meeting the charter | create version `v1` and mark evaluated |
| Feature definition or target changes | new major or minor version; new card |
| Data window or source snapshot changes | new version and fresh validation |
| Hyperparameter change | new version linked to the originating experiment |
| Editorial correction only | revise in place with dated correction note |
| Kill condition fires | mark retired or abandoned; preserve prior evidence |
| Reproduction no longer works | mark non-reproducible until repaired and reviewed |

Freeze only when data snapshot, feature set, configuration, serialized model,
and validation results are immutable. Never silently edit a frozen card to make
history look better.

## Result presentation

| Claim | Required evidence in the card |
|---|---|
| Better win probabilities | log-loss or Brier versus baseline on same folds |
| Useful probability levels | calibration curve/table and calibration error context |
| Better margin prediction | MAE or RMSE versus constant/simple rating baseline |
| Stable team ranking | out-of-time rank utility and rank stability |
| General across seasons | per-season results, not aggregate mean alone |
| General across populations | evaluated slice results and coverage statement |

State metric direction. “0.681 versus 0.693” is incomplete unless the card says
lower log-loss is better, gives sample size, and identifies the held-out period.

## Monitoring and kill conditions

Conditions must be observable, bounded, and connected to a response. Good forms
include:

- primary metric loses to the locked baseline for two consecutive review windows;
- calibration error exceeds a specified threshold for a minimum sample size;
- a required field's missingness or schema changes invalidate a feature family;
- a leakage audit becomes unresolved or fails;
- a rule, schedule, roster, or measurement regime changes beyond evaluated scope;
- population coverage moves outside the documented range;
- reproduction fails from the pinned artifacts and supported environment.

For each trigger, record owner, check cadence, minimum evidence, grace period,
and action: investigate, retrain, restrict, roll back, or retire. Avoid conditions
such as “when performance feels bad.”

## Sports-specific caveats

- State whether the model scores games, team-games, player-games, possessions,
  plays, or pitches. A doubled team-game panel is not game-level independence.
- Define treatment of ties, overtime, postseason events, neutral venues, and
  canceled or incomplete contests.
- Document schedule-strength, expansion, rule-era, roster, and source changes
  that may limit transport across seasons.
- Pre-event models must state the exact cutoff and how late injury, lineup,
  starter, weather, or market information is handled.
- Team or player identifiers must be stable across relocations and name changes.
- If probabilities drive decisions, document calibration and any threshold or
  utility assumptions; accuracy alone is insufficient.

## Hard constraints and integrity rules

1. Never describe training metrics as expected performance.
2. Never omit the baseline, decision time, grain, or primary metric.
3. Never claim generality beyond evaluated sports, seasons, and populations.
4. Never publish a card without artifact locations, an owner, and review date.
5. Never leave retirement criteria implicit.
6. Never hide leakage, validation, or calibration status.
7. Never describe exploration as production-ready.
8. Never list a reproduction command that does not match the represented version.
9. Never overwrite a frozen model history with a better-looking later result.
10. If required evidence is unavailable, state the operational consequence.

## Anti-patterns

- “Works well” with no metric, baseline, period, or denominator;
- a card written before any ordered held-out evaluation exists;
- one aggregate score with losing folds omitted;
- NFL wording, assumptions, or commands copied into another sport's card;
- kill conditions that cannot be computed;
- a feature list without as-of availability;
- a generic “bias reviewed” statement with no slice, definition, or result;
- a model filename that cannot be connected to its data and configuration.

## Worked examples

### Pre-game team-win probability

```text
Identity: home_form_logit_v3
Status: evaluated; not approved for wagering
Purpose: Estimate pre-event P(team wins) from venue and shifted form
Grain: team-game; paired rows share one contest
Decision time: scheduled start, before event-day updates
Data: completed regular-season games, 2018-2024; immutable Parquet snapshot
Validation: season walk-forward; primary metric log-loss
Baseline: constant training-fold prevalence
Result: report mean and every held-out season on identical rows
Leakage: checked; all rolling features shifted before aggregation
Limit: no injury or lineup model; cold start in early season
Kill: retire after two eligible seasons worse than baseline log-loss
Artifacts: data snapshot, feature manifest, fold metrics, predictions, model file
```

### Margin model with incomplete calibration scope

```text
Identity: pregame_margin_ridge_v1
Purpose: Predict home-team final margin before lineup lock
Primary metric: MAE versus historical-mean and simple-rating baselines
Calibration: not applicable to point predictions; interval coverage not tested
Status: experimental until prediction-interval coverage is evaluated
```

The second example does not manufacture a calibration claim; it states the
missing uncertainty check and constrains status accordingly.

## Helper

```bash
python <path-to-model-card>/scripts/write_card_stub.py \
  --name home-form-logit \
  --version v1 \
  --grain team-game \
  --out data/model_card.md
```

Fill the generated user-owned Markdown file from verified artifacts. The helper
creates structure only; it does not validate performance or approve the model.

## Output contract

A complete card has:

- every required section present;
- baseline and primary metric beside candidate results;
- aggregate, fold-level, and applicable slice evidence;
- decision time and time-safety status;
- explicit leakage and calibration status;
- concrete monitoring, retraining, and kill conditions;
- linked experiments and immutable artifact identifiers;
- exact reproduction instructions;
- version status, owner, reviewers, and next review date.

## Resources

- [`references/card_template.md`](references/card_template.md) — read when
  drafting the full card section by section.
- [`references/kill_conditions.md`](references/kill_conditions.md) — read when
  converting failure modes into measurable monitoring and retirement rules.
- `scripts/write_card_stub.py` — portable model-card scaffold writer.
