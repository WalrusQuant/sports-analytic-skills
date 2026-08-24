---
name: results-reporting
description: >
  Report sports modeling/analysis results clearly: question, methods, metrics,
  baselines, limits, and figures. Use for README sections, notebooks summaries,
  and research notes.
version: "0.1.0"
license: MIT
---

# Results Reporting (Sports DS)

Communication skill for sports data science results.

## When to use

- Finished experiment needs a writeup
- Sharing model performance with humans
- Closing an analysis thread cleanly

## When not to use

- No metrics/baselines yet
- Need formal model card structure → `model-card`

## Structure

1. Question
2. Data + grain + period
3. Methods / models
4. Validation design
5. Baselines + results
6. Interpretation
7. Limits / next tests
8. Repro pointers (scripts, seeds, package versions)

## Hard constraints

- Lead with the question and metric, not hype
- Always include baselines
- Always include period and sample size
- No betting product language
- Unknowns stay unknown

## Anti-patterns

- Metric dump without method
- Hidden filters
- “Model works” with no baseline
- Screenshots without repro

## Output contract

- [ ] Question/methods/validation present
- [ ] Baselines + results present
- [ ] Limits present
- [ ] Repro pointers present

## Handoffs

- `model-card` for durable contract
- `anti-slop-analytics` for figures
- `experiment-log` linkage
