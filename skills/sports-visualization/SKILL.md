---
name: sports-visualization
description: >
  Create honest sports-analysis figures from user-owned data, including
  distributions, rates, rating trajectories, calibration plots, and
  walk-forward metric comparisons. Use for exploration and communication.
license: MIT
metadata:
  version: "0.12.0"
---

# Sports Visualization

## Outcome

Create the smallest reproducible figure that answers a defined question without
exaggerating the evidence. Every important figure states its period, sample
size, metric definition, grain, and relevant baseline. Add uncertainty when the
claim depends on noisy differences.

This skill constructs figures. Use `anti-slop-analytics` for an independent
keep/fix/kill review and `results-reporting` for the surrounding narrative.

## When to use this skill

Use for exploratory distributions, coverage plots, model diagnostics,
calibration, ratings and form trajectories, team or player comparisons,
walk-forward results, and publication figures. Do not start with chart type:
start with the question and the unit represented by each mark.

## Required inputs

- question and intended audience;
- user-owned data or metrics artifact;
- sport, competition, grain, natural key, and period;
- relevant denominator, filters, and missing-data rules;
- metric definition and direction;
- comparison baseline and uncertainty artifact when applicable;
- desired output path and reproduction context.

If the source is a screenshot or rounded report table, do not reconstruct
precise data unless explicitly labeled approximate. Prefer the underlying table.

## Workflow

1. State the single claim or diagnostic question.
2. Validate input grain, keys, columns, types, and duplicated events.
3. Define what one mark, line, bar, or interval represents.
4. Choose the smallest chart that makes the comparison direct.
5. Add sport, population, period, denominator, units, and baseline.
6. Check axes, transforms, aggregation, bins, smoothing, missingness, and ordering.
7. Add uncertainty or fold spread if the claim compares noisy quantities.
8. Export the image and preserve the plotting command or code.
9. Write a one-sentence factual interpretation and one limitation.
10. Run an anti-slop pass before using the figure in a public claim.

## Plot selection catalog

| Question | Preferred figure | Essential checks |
|---|---|---|
| What periods are covered? | season/week coverage timeline | missing periods and schedule type |
| What is the outcome distribution? | histogram, ECDF, or quantile plot | bin sensitivity, units, ties/outliers |
| How does a rate change over time? | line or dot plot with denominators | varying `n`, rule eras, full scale |
| Is there home advantage? | home-row rate by season with interval | correct grain; do not use full doubled panel |
| How does form evolve? | as-of line or small multiples | shifted window, gaps, unequal schedules |
| Is a probability reliable? | reliability curve plus counts | bins, reference diagonal, sample size |
| Where does a margin model miss? | residual versus prediction/context | heteroskedasticity and outliers |
| How does rating evolve? | as-of trajectory with selected labels | update timing, regression, inactive teams |
| Does a candidate beat a baseline? | paired fold dots/bars or compact table | same events/folds, metric direction |
| How stable is a ranking? | ordered dots with intervals/rank distribution | opportunity and schedule strength |

Read [`references/plot_catalog.md`](references/plot_catalog.md) when routing a
question to a chart. Read
[`references/honest_labels.md`](references/honest_labels.md) before finalizing
titles, captions, annotations, and uncertainty language.

## Encoding defaults

| Comparison | Prefer | Avoid |
|---|---|---|
| Rates over seasons | line/dots or bars with `n` | cropped “dramatic” axis |
| Candidate versus baseline | paired dots, common-scale bars, or table | separate charts with different scales |
| Distribution | histogram/ECDF plus median or quantiles | mean-only summary |
| Probabilities | reliability curve and count panel | pie chart or “lock” language |
| Rankings | ordered dots or small multiples | rainbow spaghetti |
| Many teams over time | selected labeled series or faceted small multiples | unreadable 30-line legend |
| Two time series | aligned panels or indexed comparison | dual axes tuned for correlation |
| Effects | point estimate and interval | stars without magnitude |

For rates, the axis must show changes without manufacturing drama. Zero is not
mandatory for every line plot, but any restricted range must be justified and
clearly labeled. Bar length encodes magnitude and normally needs a meaningful
zero.

## Sports-specific caveats

- Team-game panels often contain complementary home and away rows. A home-win
  figure should filter `is_home == 1`; state unique-game `n`.
- Rolling features and ratings must be plotted as of the prediction timestamp,
  not after the event update.
- Unequal games played, minutes, plate appearances, or attempts can make player
  and team rates incomparable. Show opportunity thresholds or uncertainty.
- Schedule strength, postseason selection, neutral venues, overtime, ties, and
  rule changes can alter apparent trends.
- Season facets may have different lengths and missing weeks. Do not connect
  discontinuous observations as though spacing were equal.
- Calibration bins need event counts. A smooth-looking curve from small bins is
  not strong evidence.
- Fold-level model charts must retain losing folds and compare the same held-out rows.

## Honest title and caption template

```text
Title: <quantity> by <comparison> — <sport/competition>, <period>
Subtitle/caption: n=<games/events/rows>; grain=<grain>; <metric definition>;
baseline=<reference>; uncertainty=<method or unknown>; exclusions=<important filters>.
Source: <artifact>; reproduce: <script/command>.
```

Use descriptive titles such as “Held-out log-loss by season” rather than
conclusion titles such as “Model Dominates.” Put interpretation in the caption,
bounded by the observed population.

## Uncertainty and aggregation

- Use intervals appropriate to the sampling/design assumptions; name the method.
- When repeated teams, players, or games induce dependence, avoid pretending
  rows are independent. Consider grouped resampling or fold variation.
- Distinguish an unweighted season mean, an event-weighted mean, and a pooled
  metric. Label whichever is plotted.
- Do not invent error bars when only aggregate numbers exist. State uncertainty
  as unavailable and show the raw fold or season values.
- Show both numerator and denominator for important rates when feasible.

## Hard constraints and integrity rules

1. Period and denominator appear on every key figure.
2. Metric, units, sport, population, and grain are explicit when not obvious.
3. A comparative claim includes its relevant baseline.
4. Axes and transforms do not manufacture the effect.
5. Dual-axis correlation theater is prohibited.
6. Probabilities are displayed as uncertain quantities, not destiny.
7. Training metrics are never labeled held-out or walk-forward.
8. Losing folds, missing periods, and excluded groups are not silently removed.
9. Every claim-bearing figure has a reproduction path.
10. Unknown uncertainty is disclosed, not fabricated.

## Anti-patterns

- rainbow spaghetti with every team unlabeled;
- decorative 3-D, pie, gradients, or gauges;
- one hot streak presented as season truth;
- a correlation heatmap without a question;
- missing baseline in a model-comparison chart;
- smoothed lines with no method or window;
- in-sample fit presented as validation;
- cropped axes used to magnify small home-field changes;
- image exports with no source data or command.

## Standalone helpers

Install `pandas` and `matplotlib`; Parquet also needs `pyarrow` or `fastparquet`.
The table helpers accept user-owned CSV, Parquet, JSON, JSONL, or NDJSON.

For a team-game panel with `is_home` and `point_diff`:

```bash
python <path-to-sports-visualization>/scripts/plot_home_margin_hist.py \
  --input games.csv --out home_margin.png
```

For a panel with `season`, `is_home`, and binary `won`:

```bash
python <path-to-sports-visualization>/scripts/plot_home_win_rate.py \
  --input games.parquet --out home_rate.png
```

Column flags map alternate schemas. The home-win helper drops rows without an
observed season/outcome, labels each season's eligible home-row denominator,
uses a 0-to-1 rate scale, and displays 95% Wilson intervals. Those intervals
treat eligible games as Bernoulli observations and do not account for broader
season/team dependence.

For a JSON report containing a `folds` array, each row needs an explicit fold
label, held-out denominator (`n_test` by default), and candidate and baseline
metric fields:

```bash
python <path-to-sports-visualization>/scripts/plot_walkforward_metrics.py \
  --json metrics.json \
  --fold-col fold \
  --metric logistic_log_loss \
  --baseline constant_log_loss \
  --out comparison.png
```

The helper rejects duplicate fold labels and missing/nonpositive denominators,
but cannot verify that the two metric columns came from identical rows or
derive sampling uncertainty from aggregate scores. Perform the row-identity
check before plotting; its default title labels uncertainty unavailable.

## Worked examples

### Home win rate

Validate the panel is team-game grain, filter home rows, count unique contests,
and show per-season rate with denominator. Caption the figure as “home rows
only” and disclose ties or excluded games.

### Walk-forward model comparison

Plot candidate and baseline on the same y-axis for every eligible fold. State
that lower log-loss is better, retain folds where the candidate loses, and use a
table instead if small differences are difficult to read honestly.

### Team rating trajectories

Plot ratings recorded before each event update. Label a small number of relevant
teams directly, mark long inactivity gaps, and avoid interpreting a rating line
as causal player or coaching impact.

## Output contract

Return the figure path, source artifact, plotting command/code, purpose,
population and grain, period and denominator, metric/baseline, uncertainty
method, important exclusions, one bounded interpretation, and remaining limits.

## Resources

- [`references/plot_catalog.md`](references/plot_catalog.md) — read when choosing
  the visual form for a sports question.
- [`references/honest_labels.md`](references/honest_labels.md) — read when writing
  titles, captions, denominators, and uncertainty notes.
- `scripts/plot_home_margin_hist.py` — standalone home-margin distribution plot.
- `scripts/plot_home_win_rate.py` — standalone home-win-rate plot.
- `scripts/plot_walkforward_metrics.py` — standalone fold comparison plot.
