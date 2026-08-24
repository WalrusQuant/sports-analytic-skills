---
name: sports-modeling-doctrine
description: >
  Define a sports analysis or prediction question, grain, decision time,
  baselines, primary metrics, validation, and acceptance criteria before choosing
  algorithms. Use at the start of any sports modeling project.
license: MIT
metadata:
  version: "0.7.0"
---

# Sports Modeling Doctrine

## Outcome

Write a modeling charter before acquiring data or fitting models. The charter is
a user-owned artifact and is the source of truth for target, timing, evaluation,
and the shape of done.

## Workflow

1. Write the question in one sentence.
2. Name the sport, competition, population, and grain.
3. Classify the work as descriptive, explanatory, predictive, causal, or simulation.
4. For predictive work, define decision time T precisely.
5. Define the target and unit of observation without using future information.
6. Record the base rate or null expectation.
7. Name at least one naive and one strong simple baseline.
8. Lock the primary metric before fitting.
9. Choose validation that respects season and event order.
10. Define acceptance, failure, and stop conditions.

## Question types

| Type | Example | Required evidence |
|---|---|---|
| Descriptive | What happened? | coverage, denominators, uncertainty |
| Explanatory | What is associated? | design, confounding limits, effect sizes |
| Predictive | What will happen after T? | time-safe inputs, held-out evaluation |
| Causal | What would change under intervention? | identification strategy |
| Simulation | What distribution follows assumptions? | calibrated inputs, sensitivity |

## Metric defaults

| Target | Primary candidates | Baseline |
|---|---|---|
| Binary outcome | log-loss, Brier | constant prevalence, home indicator |
| Margin or continuous | MAE, RMSE | historical mean or simple rating |
| Count | Poisson deviance, MAE | historical mean count |
| Time to event | concordance plus calibration | simple survival estimate |
| Ranking | rank correlation and stability | prior rank or rating |

Accuracy is rarely sufficient for probability work. A metric must match the
decision and be computed on genuinely held-out observations.

## Non-negotiables

- Time safety: every predictive input must be knowable at decision time.
- Ordered validation: do not randomly shuffle season events by default.
- Baselines first: complexity earns its place only on held-out evidence.
- Grain integrity: never mix game, team-game, player-game, and event rows silently.
- Honest uncertainty: report variation across folds, seasons, or resamples.
- Reproducibility: save data, feature, configuration, metrics, and command artifacts.

## Charter schema

```text
question
sport_and_competition
population
grain
analysis_type
decision_time
target
base_rate_or_null
baselines
primary_metric
secondary_metrics
validation_design
data_requirements
acceptance_rule
failure_conditions
out_of_scope
```

## Helper

```bash
python <path-to-sports-modeling-doctrine>/scripts/print_charter_template.py --out data/modeling_charter.md
```

## Operating rules

- Use only the skills relevant to the question; each skill must stand alone.
- Pass explicit user-owned artifacts between skills.
- Record decisions in the charter or experiment record, not only in chat.
- Stop when the acceptance rule is met or a failure condition invalidates the work.
- Report a blocker when required timing, grain, or provenance cannot be established.

## Resources

- `references/charter_examples.md` — worked charters
- `references/good_enough.md` — acceptance and stopping rules
- `references/skill_path.md` — optional skill handoffs
- `scripts/print_charter_template.py` — portable charter writer
