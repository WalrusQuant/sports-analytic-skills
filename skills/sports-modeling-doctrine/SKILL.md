---
name: sports-modeling-doctrine
description: >
  Define a sports analysis or prediction question, grain, decision time,
  baselines, primary metrics, validation, and acceptance criteria before choosing
  algorithms. Use at the start of any sports modeling project.
license: MIT
metadata:
  version: "0.12.0"
---

# Sports Modeling Doctrine

## Outcome

Write a modeling charter before acquiring data or fitting models. The charter is
a user-owned source of truth for the question, target, timing, evaluation, and
shape of done.

Before code, lock the scientific contract:

- what question is being answered;
- what one row represents;
- what is knowable at decision time;
- what baseline counts as evidence of value;
- how success will be measured out of time;
- what result causes acceptance, revision, or stopping.

If these fields are not named, do not fit a model.

## When to use this skill

Use it when starting or reframing a sports analysis, deciding what “good” means,
reviewing whether a result is evaluable, or preventing exploratory work from
quietly becoming a predictive claim.

After the charter, use only the relevant specialist skills: a public-source
loader for acquisition, `eda-sports` for data understanding, `feature-rules` for
time-safe predictors, `baseline-models` for reference models, and the relevant
statistical, predictive, rating, simulation, or validation skill.

## Question types

| Type | Core question | Required evidence | Common overreach |
|---|---|---|---|
| Descriptive | What happened? | coverage, denominators, uncertainty | treating the sample as every era/population |
| Explanatory | What is associated? | design, effects, uncertainty, confounding limits | causal language |
| Predictive | What will happen after time `T`? | time-safe inputs and ordered holdout | explaining coefficients as causes |
| Causal | What changes under an intervention? | identification strategy and assumptions | using prediction alone |
| Ranking | Who is strongest as of `T`? | future utility, schedule context, rank stability | treating point ranks as certain |
| Simulation | What distribution follows assumptions? | calibrated inputs and sensitivity | reporting simulated precision as observed fact |

Do not mix explanatory and predictive success. A stable association need not
improve forecasts, and a useful predictor need not identify a causal mechanism.

## Charter workflow

1. Write the question in one sentence.
2. Name sport, competition, population, era, and exclusions.
3. Define grain: game, team-game, player-game, possession, play, pitch, or other.
4. Classify the analysis type using the table above.
5. For predictive, ranking, or prospective simulation work, define decision
   time `T` and forecast horizon precisely.
6. Define target or estimand, units, label rules, and treatment of ties or missing outcomes.
7. Record base rate, null expectation, or incumbent process.
8. Name at least one naive and one strong simple baseline.
9. Lock the primary metric and its direction before fitting.
10. Choose validation that respects event, season, and availability order.
11. Define data requirements, minimum coverage, and provenance standards.
12. Write acceptance, failure, revision, and stop conditions.
13. Record out-of-scope decisions and unsupported uses.

## Grain and decision-time contract

For each proposed field, be able to answer:

```text
row grain: <what one row represents>
entity/event key: <natural key>
decision time T: <timestamp or event boundary>
forecast horizon: <what future interval is predicted>
feature available by T: <yes/no and source timestamp>
target observed after T: <yes/no>
paired/dependent rows: <shared games, players, series, seasons>
```

Sports data routinely contain doubled team-game rows, postgame summaries,
revised injury reports, end-of-season aggregates, and ratings updated after the
event. Column names do not prove availability. Define an as-of rule.

## Baseline ladder

| Level | Example | Purpose |
|---|---|---|
| Null | constant training prevalence or historical mean | proves value beyond no differentiation |
| Structural | venue indicator, prior rank, or league average by context | captures obvious domain structure |
| Strong simple | shifted form, simple rating, or regularized linear/logistic model | tests whether complexity earns its cost |
| Incumbent | current operational forecast or public reference | measures practical replacement value |

Lock baseline definitions, training windows, and missing-data behavior before
candidate tuning. All models must be scored on identical held-out rows.

## Metric defaults

| Target | Primary candidates | Baseline | Important secondary evidence |
|---|---|---|---|
| Binary outcome | log-loss, Brier | prevalence, venue/simple rating | calibration and fold spread |
| Margin/continuous | MAE, RMSE | historical mean or simple rating | residual distribution and interval coverage |
| Count | Poisson deviance, MAE | historical mean count | dispersion and zero behavior |
| Time to event | proper survival score/concordance | simple survival estimate | calibration by horizon |
| Ranking | future-result correlation or utility | prior rank/rating | rank stability and uncertainty |
| Simulation | distributional score or coverage | simple empirical distribution | sensitivity to assumptions |

Accuracy is rarely sufficient for probability work. Match the metric to the
decision, define its direction, and compute it only on genuinely held-out data.

## Validation defaults

Ordered sports events usually require expanding-window or rolling-origin
validation. A default season walk-forward design trains on seasons before `s`
and evaluates on season `s`. When a sport lacks clean seasons, split by event
time with explicit gaps or embargoes where labels/features overlap.

Random row shuffles are not the default because they can mix future roster,
team-strength, schedule, and feature information into training. Group shared
contests together, and account for repeated teams or players when estimating
uncertainty.

## Acceptance and stopping rules

A predictive candidate is normally worth keeping only if it:

- beats locked baselines on the mean primary metric;
- improves in a meaningful majority of eligible folds or has a justified pooled result;
- passes time-safety and leakage checks;
- avoids catastrophic calibration if probabilities are quoted;
- remains useful under relevant era, team, player, or event slices;
- justifies its complexity and maintenance burden.

For explanatory work, require stable effect direction, honest uncertainty, and
bounded claims. For simulation, require input calibration and sensitivity.

Read [`references/good_enough.md`](references/good_enough.md) when setting the
acceptance rule. Stop when the rule is met, when a failure condition invalidates
the work, or when further complexity does not earn material held-out value.

## Charter schema

```text
question
sport_and_competition
population_and_exclusions
grain_and_natural_key
analysis_type
decision_time_and_horizon
target_or_estimand
base_rate_or_null
naive_and_strong_baselines
primary_metric_and_direction
secondary_metrics
validation_design
data_requirements_and_provenance
uncertainty_plan
acceptance_rule
failure_and_stop_conditions
out_of_scope_and_prohibited_uses
required_artifacts
```

## Worked charters

### Pre-game team-win probability

```text
Question: Do venue and shifted form improve P(team wins)?
Sport/population: NFL completed regular-season games, 2018-2024
Grain: team-game; two paired rows per contest
Decision time: scheduled kickoff
Target: won; ties reported separately
Baselines: constant training prevalence; venue-only logistic
Primary metric: held-out log-loss, lower is better
Validation: season walk-forward; contest rows remain together
Acceptance: beat both baselines in mean and at least five of seven folds
Failure: any feature not provably available before kickoff
Out of scope: causal claims and wagering profitability
```

### Player next-game count

```text
Question: Predict a starter's strikeouts in the next start.
Grain: player-game
Decision time: first pitch
Target: strikeouts in that start
Baselines: trailing shifted mean; opponent strikeout-allowed mean
Primary metric: MAE
Validation: date walk-forward with player histories truncated at T
Cold start: separate rule and reporting slice
```

Read [`references/charter_examples.md`](references/charter_examples.md) for
additional compact NFL, NBA, and MLB patterns.

## Non-negotiables and integrity rules

1. Time order matters; random event shuffles need explicit justification.
2. Features must be legal at `T` for prospective claims.
3. Baselines are defined before candidate models.
4. The primary metric is locked before inspecting test folds.
5. Grain changes require explicit aggregation and key validation.
6. Candidate and baseline use identical held-out populations.
7. Failures and non-improvement are recorded as valid results.
8. Strong claims require a leakage audit and honest uncertainty.
9. Public data does not eliminate provenance, licensing, or snapshot duties.
10. Scope does not expand silently after favorable results appear.
11. Use the simplest model that meets the charter.
12. Record decisions and artifacts outside ephemeral chat.

## Anti-patterns

- choosing an algorithm before defining the decision;
- feature soup without an availability timestamp;
- calling one hot season “generalization”;
- changing the primary metric after seeing held-out results;
- treating each team-game row as an independent game;
- copying the same assumptions across sports with different schedules or rules;
- continuing to tune after the test window becomes familiar;
- declaring victory because a complex model beats the null but not a strong simple baseline;
- producing probabilities without a calibration plan.

## Helper

```bash
python <path-to-sports-modeling-doctrine>/scripts/print_charter_template.py \
  --out data/modeling_charter.md
```

Fill the user-owned template before data acquisition or fitting. The helper
does not choose the question, baseline, or acceptance rule.

## Operating and handoff rules

- Use only the skills relevant to the charter; every skill must stand alone.
- Pass explicit user-owned artifacts between acquisition, analysis, and reporting steps.
- Keep the charter current when a justified scope decision changes.
- Re-charter rather than quietly changing target, grain, or decision time.
- Report a blocker when timing, grain, provenance, or evaluation cannot be established.

For optional downstream routing, read
[`references/skill_path.md`](references/skill_path.md). It is a decision aid,
not a requirement to invoke every listed skill.

## Output contract

Return or save the completed charter with question, type, sport/population,
grain/key, decision time, target, baselines, primary metric, validation,
uncertainty, acceptance/failure rules, out-of-scope uses, and required artifacts.
Do not return an algorithm recommendation without this contract.

## Resources

- [`references/charter_examples.md`](references/charter_examples.md) — read for
  sport- and target-specific charter examples.
- [`references/good_enough.md`](references/good_enough.md) — read when defining
  acceptance, failure, and stopping rules.
- [`references/skill_path.md`](references/skill_path.md) — read when choosing
  optional specialist handoffs after the charter.
- `scripts/print_charter_template.py` — portable charter writer.
