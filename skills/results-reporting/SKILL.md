---
name: results-reporting
description: >
  Report sports analysis and modeling results with the question, data, methods,
  validation, baselines, metrics, interpretation, limits, figures, and
  reproduction pointers. Use for research notes, reports, and final answers.
license: MIT
metadata:
  version: "0.12.0"
---

# Results Reporting

## Outcome

Turn user-owned metrics and analysis artifacts into a report a stranger can
trust. Every quantitative claim must be traceable to data, validation, and
reproduction evidence. Separate observed results from interpretation, and
separate predictive performance from explanation or causality.

A results report tells the story of one evaluation. A model card is the durable
operating contract; an experiment log is the trial history.

## When to use this skill

Use it for notebook summaries, research notes, README result sections, internal
reports, public writeups, and final answers after an analysis. If there are no
metrics or baselines yet, stop and produce the evaluation artifacts first.

Use `model-card` for a frozen reusable model, `anti-slop-analytics` for a visual
honesty review, and `model-interpretation` when the main question is why errors
or predictions occurred.

## Evidence inventory

Collect, when available:

- modeling charter or exact question;
- source manifest, data snapshot, schema, filters, and sample counts;
- target, decision time, feature definitions, and leakage result;
- baseline and candidate configurations;
- fold assignments, predictions, aggregate and fold-level metrics;
- calibration, slice, sensitivity, and uncertainty outputs;
- figures and their source tables;
- environment, seed, code version, and exact reproduction command.

Missing evidence is a limitation, not permission to infer. Label it as missing
and narrow the claim accordingly.

## Required structure

1. **Executive result** — one bounded sentence with primary metric and baseline.
2. **Question** — sport, population, target or estimand, and decision context.
3. **Data** — source, grain, period, sample size, filters, missingness, snapshot.
4. **Methods** — labels, features, baseline, candidate, and assumptions.
5. **Validation** — split logic, folds, metric definitions, and uncertainty.
6. **Results** — primary metric first, baseline beside candidate, then folds and slices.
7. **Interpretation** — what the evidence supports and does not support.
8. **Limitations and failed checks** — including unsupported uses.
9. **Figures and tables** — each with denominator, period, baseline, and source.
10. **Reproduction** — artifacts, code/environment version, and commands actually used.

Read [`references/templates.md`](references/templates.md) when selecting a short
chat format or a full Markdown note. Before delivery, run the quality gate in
[`references/writeup_checklist.md`](references/writeup_checklist.md).

## Workflow

1. Lock the exact question, target or estimand, and decision time.
2. Inventory data, model, metrics, prediction, figure, and audit artifacts.
3. Verify that candidate and baseline use identical held-out rows and folds.
4. State sport, competition, grain, period, sample size, filters, and missingness.
5. Describe methods at the level required to reproduce them.
6. Report the predeclared primary metric first with baseline and direction.
7. Add uncertainty or fold spread; retain losing folds, nulls, and failed checks.
8. Separate aggregate, fold-level, slice, calibration, and sensitivity results.
9. Interpret magnitude and stability without causal or operational overreach.
10. List limitations, omitted information, and populations outside evaluation.
11. Include exact artifact paths and commands supplied by the user.
12. Audit figures and cross-check every number against its source artifact.

## Metric presentation rules

| Target or claim | Lead with | Required comparison/context |
|---|---|---|
| Win probability | log-loss or Brier | constant prevalence and strong simple baseline |
| Probability reliability | calibration curve/table and error | sample size per bin and discrimination separately |
| Binary classification | proper score; accuracy secondary | base rate, threshold, and confusion counts |
| Margin or continuous outcome | MAE or RMSE | constant or simple domain baseline |
| Counts | deviance or appropriate score; MAE if useful | naive count baseline and distribution assumption |
| Ranking | out-of-time correlation or utility | prior rank/rating plus stability and uncertainty |
| Explanatory effect | estimate and interval | design assumptions, controls, and confounding limits |
| Simulation | distribution, quantiles, calibration | assumptions and sensitivity to uncertain inputs |

Always state sample size, evaluation period, fold aggregation, and which
direction is better. Never make accuracy the only evidence for probability
quality.

## Results table pattern

Keep baseline and candidate adjacent:

| Fold/season | `n` | Baseline | Candidate | Candidate minus baseline | Better? |
|---|---:|---:|---:|---:|---|
| 2022 | ... | ... | ... | ... | ... |
| 2023 | ... | ... | ... | ... | ... |
| Mean or pooled | ... | ... | ... | ... | ... |

Define whether the summary is an unweighted fold mean, event-weighted mean, or
pooled score. Those quantities need not agree. For loss metrics, make the sign
of “candidate minus baseline” explicit so negative is not misread.

## Interpretation ladder

Move only as far as the evidence allows:

1. **Observed:** “Held-out log-loss was 0.681 versus 0.693.”
2. **Comparative:** “The candidate improved the score by 0.012 on these rows.”
3. **Stability:** “It improved in five of seven season folds.”
4. **Generalization:** “Results support use within the evaluated competition and eras.”
5. **Operational value:** requires a defined decision rule, costs, and utility.
6. **Causal explanation:** requires a causal design, not a predictive model alone.

Do not jump from level 1 to level 5 or 6. A statistically visible difference may
still be operationally trivial; a useful predictor need not be a causal driver.

## Sports-specific reporting traps

- At team-game grain, two rows may represent one contest. Report both row count
  and unique-game count when dependence matters.
- Overall win rate on a complementary two-row panel is near 0.5 by construction;
  home advantage requires home rows or game grain.
- Distinguish regular season, postseason, neutral venues, overtime, and ties.
- State whether metrics are pooled across leagues, competitions, seasons, teams,
  or players and whether weighting reflects exposure.
- Report cold-start behavior for early-season form or ratings.
- Disclose rule, schedule, roster, tracking, and source-definition changes.
- Player leaderboards require opportunity thresholds and survivor/selection caveats.
- A probability report is incomplete when calibration was not checked; say so.

## Required artifact schema

The bundled renderer accepts JSON with this minimum shape:

```json
{
  "title": "Home-form win model",
  "analysis_type": "predictive",
  "question": "Does prior form improve held-out win probabilities?",
  "data": {"source": "immutable schedule snapshot", "sport": "NFL", "grain": "team-game", "period": "2021-2023 regular seasons", "n": 1632},
  "methods": {"target": "won", "decision_time": "kickoff", "baseline": "constant rate", "candidate": "logistic"},
  "validation": {"design": "season walk-forward", "primary_metric": "log_loss", "metric_direction": "lower", "comparison_population": "identical held-out game rows"},
  "results": {"baseline_log_loss": 0.693, "candidate_log_loss": 0.681},
  "interpretation": "The candidate improved held-out log-loss modestly.",
  "limits": ["Public injury information was not included."],
  "reproduction": {
    "artifacts": ["data/metrics.json", "data/predictions.csv"],
    "command": "python run_analysis.py --config analysis.json"
  }
}
```

Additional fields are allowed. The renderer requires an explicit
`analysis_type`, source, sport, grain, period, positive `n`, non-empty results,
limitations, and a reproduction artifact pointer. Predictive and ranking modes
also require a baseline, candidate, decision/as-of time, validation design,
primary metric and direction, and a statement that defines the comparison
population. Descriptive, explanatory, causal, and simulation reports use
mode-specific method fields and are not forced into a predictive baseline or
walk-forward schema. Reproduction metadata may contain whatever the user
actually has; never invent a command.

## Hard constraints and integrity rules

1. Never report a candidate metric without its locked baseline beside it.
2. Never report only the best fold, segment, hyperparameter search, or seed.
3. Never compare metrics computed on different populations without disclosure.
4. Never call a model calibrated from discrimination metrics alone.
5. Never omit negative, null, unstable, or failed results.
6. Never present training fit as held-out or forward performance.
7. Never mix sports or grains without explicit labels and aggregation rules.
8. Never manufacture reproduction commands, package versions, or audit status.
9. Never imply causal explanation from observational prediction.
10. If leakage or calibration was not checked, say so near the main result.

## Anti-patterns

- leaderboard screenshot with no method or source;
- “the model is good” with no baseline;
- average metrics with no fold table;
- a long methods preamble before the actual result;
- quietly dropping the season that lost;
- reporting tiny metric improvements as economically meaningful without utility;
- presenting rounded prose numbers that disagree with the attached table;
- using figure titles to overstate what cautious body text admits.

## Worked report lead

```text
Question: Do shifted pre-event form features improve team-win probabilities?
Data: NFL team-game panel, 2018-2024, completed regular-season games; report
both team-row and unique-game counts.
Validation: season walk-forward; primary metric log-loss, lower is better.
Result: candidate 0.681 versus constant baseline 0.693 on identical held-out
rows; candidate won five of seven folds.
Interpretation: modest predictive improvement in the evaluated seasons, not a
causal claim and not evidence of wagering profitability.
Limits: no injury model; early-season cold start; calibration status reported
separately.
```

## Helper

```bash
python <path-to-results-reporting>/scripts/render_results_report.py \
  --json data/results.json \
  --out data/results_report.md
```

Edit and verify the rendered draft. A valid schema does not prove that the
metrics are comparable, the interpretation is justified, or the report is
complete.

## Output contract

Return the executive result, question, data, methods, validation, baseline and
candidate results, fold/slice evidence, interpretation, limitations, figure
manifest, artifact manifest, and reproduction instructions. Match report length
to the audience without dropping the evidence chain.

## Resources

- [`references/templates.md`](references/templates.md) — read when choosing
  between concise and full narrative forms.
- [`references/writeup_checklist.md`](references/writeup_checklist.md) — read
  for the final evidence and honesty pass.
- `scripts/render_results_report.py` — validated standalone JSON-to-Markdown renderer.
