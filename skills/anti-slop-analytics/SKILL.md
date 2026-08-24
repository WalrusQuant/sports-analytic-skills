---
name: anti-slop-analytics
description: >
  Review sports figures, tables, notebooks, and reports for chartjunk, fake
  certainty, cropped axes, baseline erasure, metric laundering, and weak
  reproducibility. Use when asked to clean up or audit analytical presentation.
license: MIT
metadata:
  version: "0.7.0"
---

# Anti-Slop Analytics

## Outcome

Produce an item-by-item keep, fix, or kill review. Every retained item must have
a defensible claim, population, period, denominator, baseline, uncertainty
statement, and reproduction pointer.

## Inputs

- the figure, table, notebook, or report
- the claim each item is intended to support
- the underlying user-owned data or metrics artifact when available
- the decision context and audience

If an artifact is missing, audit what is visible and label every unverifiable
property as unknown. Do not infer provenance from appearance.

## Workflow

1. Inventory every figure and table with its filename or stable identifier.
2. Write the single claim each item supports. Kill items with no decision-relevant claim.
3. Verify sport, grain, period, sample size, exclusions, and denominator.
4. Check that the comparison includes the relevant null or baseline.
5. Inspect axes, scales, bins, smoothing, color, ordering, and annotations.
6. Separate in-sample, held-out, and forward-looking results.
7. Require uncertainty or explicitly state why it is unavailable.
8. Trace the item to a user-owned data file, metrics file, notebook, or command.
9. Assign keep, fix, or kill and prescribe the smallest honest replacement.

## Failure catalog

| Failure | Why it fails | Preferred replacement |
|---|---|---|
| Cropped quantitative axis | exaggerates small changes | zero or justified domain range |
| Dual axes | implies a relationship through scaling | aligned panels or indexed series |
| Ranking without uncertainty | treats noise as order | intervals or stability ranks |
| Accuracy without base rate | hides class imbalance | baseline plus proper score |
| Mean without distribution | hides tails and skew | interval, quantiles, or distribution |
| Unlabeled smoothing | conceals transformation | label method and parameters |
| Decorative 3-D or gradients | adds non-data ink | flat marks with direct labels |
| Screenshot-only evidence | cannot be checked | exported artifact plus source pointer |

## Verdict rubric

- **Keep:** claim, scope, baseline, uncertainty, and provenance are all clear.
- **Fix:** the underlying calculation is usable but presentation can mislead.
- **Kill:** the item is wrong-grain, unverifiable, redundant, or decision-irrelevant.

## Hard constraints

- Never remove a baseline because it makes a result look weaker.
- Never mix training and held-out metrics in one unlabeled series.
- Never label a probability as calibrated without a calibration check.
- Never imply causality from observational association.
- Never hide missing data, filters, or excluded seasons.

## Output contract

Return:

1. an executive verdict;
2. an audit row per item;
3. exact replacement instructions for every fix;
4. a list of missing evidence;
5. the artifact paths or commands needed to reproduce retained items.

## Helper

Run the bundled helper by absolute path or from this skill directory:

```bash
python <path-to-anti-slop-analytics>/scripts/figure_audit_template.py --out data/figure_audit.md
```

The helper writes a user-owned Markdown checklist and requires no project package.

## Resources

- `references/slop_catalog.md` — expanded failure patterns
- `references/replacements.md` — honest visual replacements
- `scripts/figure_audit_template.py` — portable audit template writer
