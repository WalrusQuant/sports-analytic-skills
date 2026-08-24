---
name: anti-slop-analytics
description: >
  Kill analytics presentation slop in sports work: chartjunk, fake certainty,
  cropped axes, vanity dashboards, baseline erasure, and unreproducible
  screenshot science. Use when reviewing figures, tables, notebooks, or report
  visuals for sports modeling. Includes a caption/figure audit checklist script.
version: "0.3.0"
license: MIT
metadata:
  version: "0.3.0"
---

# Anti-Slop Analytics (Sports)

## Overview

Sports analytics fails in public when visuals lie softer than the text. This skill enforces honest presentation for sports modeling results.

## When to Use This Skill

- Reviewing charts, tables, dashboards, or notebook outputs
- Preparing figures for README, posts, papers, or model cards
- User asks to “make it look more impressive”
- Suspected vanity metrics or cropped axes
- Pairing with `results-reporting` before publishing

## When Not to Use

- Designing validation/metrics from scratch → `validation-design`
- Leakage mechanics → `leakage-audit`
- No visual/table exists yet

---

## Slop Catalog (fail these)

1. **Certainty cosplay** — no uncertainty, no sample size, huge font conclusion
2. **Axis crimes** — truncated axes that manufacture drama
3. **Time cherry-pick** — zoom to the winning window only
4. **Metric laundering** — flashy secondary metric hides primary failure
5. **Baseline erasure** — model curve with no reference
6. **Legend fog** — unreadable encodings, 12 colors, no point
7. **Dual-axis trickery** — unrelated series forced into fake correlation
8. **Heatmap theater** — giant correlation mats with no hypothesis
9. **3D / pie distraction** for simple comparisons
10. **Screenshot science** — unreproducible UI grabs as proof
11. **Probabilities as destiny** — 53% shown like a lock
12. **One hot streak highlight reel** as season truth

---

## Workflow

1. Identify the intended claim of each visual.
2. Check encoding honesty (axes, scales, filters, missing baselines).
3. Check statistical honesty (n, period, uncertainty, selection).
4. Check claim alignment (does visual match the evidence?).
5. Mark each visual: `keep` / `fix` / `kill`.
6. Rewrite titles/captions to state what was measured.
7. Prefer one clear visual over five decorative ones.

```bash
python skills/anti-slop-analytics/scripts/figure_audit_template.py --out data/figure_audit.md
```

---

## Replacement Defaults

| Instead of | Prefer |
|---|---|
| Rainbow equity-style curve only | metric table + baseline deltas + period notes |
| Pie charts for model compare | dot/bar with shared baseline |
| Giant feature importance flex | top drivers + stability caveat |
| Smooth marketing gradient cards | plain tables with n and dates |
| “Insight” callout boxes | falsifiable sentence + limit |

---

## Hard Constraints

1. Never truncate axes to manufacture an effect without explicit warning (default: don’t).
2. Never drop losing segments silently.
3. Never present in-sample curves as validation.
4. Every key figure needs: period, n (or event count), metric definition.
5. If uncertainty is unknown, say unknown — do not draw fake error bars.

---

## Anti-Patterns

- Dashboard makeup on a weak model
- Annotation spam that tells viewers what to feel
- Color as argument
- One magical chart carrying the whole claim
- UI skins over missing method

---

## Output Contract

- [ ] Each visual scored keep / fix / kill
- [ ] Specific slop issues named
- [ ] Replacement guidance given
- [ ] Caption/title rewrites where needed
- [ ] Remaining misread risk stated

---

## Worked Example

**Input:** chart titled “Dominant Model” showing cumulative accuracy from one season, y-axis starts at 0.55, no baseline, no sample size.

**Audit:** axis crime + cherry-pick + baseline erasure + overclaim title → `kill`

**Replace with:** walk-forward log-loss vs baselines by season; title “Walk-forward log-loss vs baselines (2019–2024)”.

---

## Bundled Resources

### scripts/

- `figure_audit_template.py` — markdown audit checklist emitter

### references/

- `slop_catalog.md`

---

## Related Skills

- `results-reporting`
- `sports-visualization`
- `calibration-check`
- `model-interpretation`
- `model-card`
