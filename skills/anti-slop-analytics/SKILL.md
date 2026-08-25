---
name: anti-slop-analytics
description: >
  Review sports figures, tables, notebooks, and reports for chartjunk, fake
  certainty, cropped axes, baseline erasure, metric laundering, and weak
  reproducibility. Use when asked to clean up or audit analytical presentation.
license: MIT
metadata:
  version: "0.12.0"
---

# Anti-Slop Analytics

## Outcome

Produce an item-by-item `keep`, `fix`, or `kill` review. Every retained figure or
table must make a defensible claim and disclose its population, period,
denominator, comparison baseline, uncertainty, and reproduction pointer.

Pretty is optional. Honest is required. Presentation cannot rescue a weak
design, a losing model, or an unverifiable calculation.

## When to use this skill

Use it when reviewing:

- exploratory or diagnostic plots;
- model-comparison and calibration figures;
- dashboards, notebooks, reports, papers, or public posts;
- requests to make results look cleaner, stronger, or more impressive;
- any visual whose design may conceal a weak baseline or unstable result.

If no visual or table exists, create the analytical artifact first. Use
`sports-visualization` for figure construction, `validation-design` for the
evaluation itself, and `results-reporting` for the full narrative. This skill
audits presentation; it does not repair the underlying study by relabeling it.

## Inputs and evidence

Request or inspect:

- the figure, table, notebook, or report;
- the one claim each item is intended to support;
- the underlying user-owned data or metrics artifact when available;
- the decision context and audience;
- the plotting command, script, or notebook cell;
- relevant filters, exclusions, and fold definitions.

If evidence is missing, audit what is visible and mark unverifiable properties
as `unknown`. Never infer provenance, sample size, uncertainty, or held-out
status from visual polish.

## Audit workflow

1. Inventory every figure and table with a filename or stable identifier.
2. Write the single decision-relevant claim each item is meant to support.
3. Verify sport, competition, grain, period, population, sample size,
   exclusions, and denominator.
4. Confirm that the plotted quantity matches the title, caption, and claim.
5. Check that a relevant null, naive model, or incumbent baseline is visible.
6. Inspect axes, transformations, scales, bins, smoothing, color, ordering,
   facets, and annotations.
7. Separate training, in-sample, held-out, and forward-looking evidence.
8. Inspect statistical honesty: uncertainty, multiplicity, selection, missing
   segments, and sensitivity to the chosen time window.
9. Trace the item to a user-owned data file, metrics file, notebook, or command.
10. Assign `keep`, `fix`, or `kill`; prescribe the smallest honest replacement.

## Failure catalog

| Failure | Why it fails | Preferred replacement |
|---|---|---|
| Certainty without `n` | hides evidence volume | report denominator and interval or fold spread |
| Cropped quantitative axis | exaggerates small changes | zero or a justified domain range with disclosure |
| Cherry-picked time window | turns a hot streak into a general claim | full relevant period plus sensitivity window |
| Baseline erasure | prevents judging incremental value | plot candidate beside locked baseline |
| Metric laundering | promotes a flattering secondary metric | lead with the predeclared primary metric |
| Training as validation | overstates generalization | clearly labeled held-out or walk-forward results |
| Ranking without uncertainty | treats noisy order as stable | intervals, rank distributions, or stability summaries |
| Accuracy without base rate | hides class imbalance and probability quality | baseline plus log-loss or Brier score |
| Mean without distribution | hides tails, skew, and fold losses | quantiles, interval, distribution, or fold table |
| Unlabeled smoothing | conceals a transformation | state method, window, and parameters |
| Dual axes | manufactures visual correlation through scaling | aligned panels or indexed series |
| Giant correlation heatmap | substitutes volume for a hypothesis | selected relationships with purpose and uncertainty |
| Decorative 3-D, pie, or gradients | adds non-data ink and distorts comparison | flat marks, direct labels, or a small table |
| Screenshot-only evidence | cannot be reproduced or checked | exported artifact plus source and command |
| Probability framed as destiny | converts uncertainty into a lock | probability plus calibration and decision context |
| Sport context removed | makes grain and population ambiguous | sport, competition, grain, and period in label/caption |

For additional examples, read
[`references/slop_catalog.md`](references/slop_catalog.md) when classifying a
suspect item and [`references/replacements.md`](references/replacements.md)
when choosing a redraw.

## Verdict rubric

| Verdict | Use when | Required action |
|---|---|---|
| `keep` | claim, scope, baseline, uncertainty, and provenance are clear | retain; tighten caption only if needed |
| `fix` | calculation is usable but the presentation can mislead | specify exact axis, label, baseline, or encoding repair |
| `kill` | wrong grain, wrong evidence, unverifiable, redundant, or decision-irrelevant | remove or replace with a new artifact |

If a decorative chart can be fixed only by changing its core claim, kill it and
redraw from the underlying evidence.

## Sports-specific checks

- A doubled team-game panel has two rows per contest. Do not report its overall
  win rate as home advantage; filter home rows or return to game grain.
- Team and player rankings often have unequal schedules and sample sizes. Show
  opportunity, exposure, or shrinkage rather than raw order alone.
- Season averages can hide rule, schedule, roster, or measurement changes.
  Label eras and test whether the conclusion survives them.
- Probabilities require calibration evidence. Discrimination alone does not
  show that a displayed 70% forecast occurs about 70% of the time.
- Rolling form and rating lines must be as-of series. Centered windows or
  post-event updates cannot support a pre-event claim.
- Fold charts must use identical held-out events for candidate and baseline.
  A bar comparison is invalid if populations differ.
- Ties, overtime, postseason games, and canceled events need visible treatment
  when they change denominators or target definitions.

## Replacement defaults

| Instead of | Prefer |
|---|---|
| Cumulative accuracy hero curve | fold-level proper score with baseline deltas |
| Pie chart for model comparison | paired dots, bars on a common scale, or table |
| Feature-importance spectacle | stable top drivers with method and caveat |
| Smooth dashboard cards | compact metrics table with `n`, dates, and baseline |
| “Insight” callout | falsifiable sentence plus limitation |
| Single-season highlight | full walk-forward table with losing folds retained |
| Thirty-team rainbow spaghetti | small multiples, selected labeled series, or ranks with uncertainty |

## Caption repair template

Use a factual caption that answers:

```text
What: <metric or quantity and units>
Who/where: <sport, competition, population, grain>
When: <period>
Evidence: n=<denominator>; <baseline or null>
Uncertainty: <interval, fold spread, or explicitly unknown>
Interpretation: <bounded claim>
Source: <artifact and reproduction pointer>
```

Avoid conclusion-first titles such as “Dominant Model.” Prefer a measurable
title such as “Held-out log-loss by season versus constant baseline.”

## Hard constraints and integrity rules

1. Never truncate an axis to manufacture an effect without conspicuous,
   defensible disclosure; default to an honest comparison scale.
2. Never drop losing folds, teams, segments, or seasons silently.
3. Never present in-sample curves as validation.
4. Every key item needs period, denominator, metric definition, sport, and grain.
5. If uncertainty is unknown, say `unknown`; do not invent error bars.
6. A baseline is required whenever a comparative model claim is made.
7. A reproduction path is required for an item used in a public claim.
8. Never imply causality from observational association.
9. Never label probabilities calibrated without a calibration check.
10. Never hide missing data, filters, exclusions, or changed definitions.

## Anti-patterns

- dashboard makeup on a weak model;
- annotation spam that tells viewers what to feel;
- color used as the argument;
- one magical chart carrying the entire claim;
- a UI skin covering a missing method;
- hiding the constant baseline because it makes the result look weaker;
- dense visuals whose only purpose is to signal sophistication;
- rebuilding a chart from rounded report numbers when source metrics exist.

## Worked audit

**Input:** A chart titled “Dominant Model” shows cumulative accuracy from one
season. The y-axis begins at 0.55, there is no base-rate line, no sample size,
and no underlying metrics file.

**Verdict:** `kill`.

**Reasons:** axis distortion, cherry-picked period, baseline erasure, metric
laundering, overclaiming title, and missing provenance.

**Replacement:** Show held-out log-loss by season for the candidate and locked
baseline on identical events; add fold sample sizes and a factual title. If the
source metrics cannot be recovered, report the evidence as unverifiable rather
than recreating precise values from the screenshot.

When a suitable metrics JSON already contains a `folds` array, an honest
comparison can be drawn with the standalone visualization helper:

```bash
python <path-to-sports-visualization>/scripts/plot_walkforward_metrics.py \
  --json data/metrics.json \
  --metric logistic_log_loss \
  --baseline constant_log_loss \
  --out data/walkforward_log_loss.png
```

Then audit that exported artifact and its underlying JSON.

## Helper

Run the bundled helper by absolute path or from this skill directory:

```bash
python <path-to-anti-slop-analytics>/scripts/figure_audit_template.py \
  --title "NBA walk-forward log-loss" \
  --claim "Candidate improves held-out log-loss versus the locked baseline" \
  --out data/figure_audit.md
```

The helper writes a user-owned Markdown checklist and requires no project
package. It creates an audit scaffold; it does not decide the verdict.

## Output contract

Return:

1. an executive verdict;
2. one audit row per item with `keep`, `fix`, or `kill`;
3. the named failure patterns and evidence for each verdict;
4. exact replacement instructions, including captions, for every fix;
5. a list of missing or unverifiable evidence;
6. the remaining misread risk after repair;
7. artifact paths or commands needed to reproduce every retained item.

## Resources

- [`references/slop_catalog.md`](references/slop_catalog.md) — read when a
  visual needs a named failure classification.
- [`references/replacements.md`](references/replacements.md) — read when
  selecting the smallest honest redraw.
- `scripts/figure_audit_template.py` — portable audit-template writer.
