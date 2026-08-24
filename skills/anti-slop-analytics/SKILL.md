---
name: anti-slop-analytics
description: >
  Kill analytics presentation slop: chartjunk, fake certainty, cropped
  reality, and vanity dashboards. Use when reviewing figures, tables,
  notebooks, or report visuals for sports-modeling work.
version: "0.1.0"
license: MIT
---

# Anti-Slop Analytics

Comms/presentation skill. Sports analytics fails in public when the visuals
lie softer than the text. This skill enforces honest presentation.

## When to use

- Reviewing charts, tables, dashboards, or notebook outputs
- Preparing figures for README, posts, papers, or model cards
- User asks to “make it look more impressive”
- Suspected vanity metrics or cropped axes
- Pairing with `results-reporting` before publishing

## When not to use

- Designing validation/metrics from scratch → `validation-design`
- Leakage mechanics → `leakage-audit`
- Claim-level adjudication → `doctrine`
- Tip-shop requests → `ethics` refuse

## Required inputs

- The figure/table/dashboard or a precise description
- The claim it is supposed to support
- Sample size / period if available
- Claim level earned

## Slop catalog (fail these)

1. **Certainty cosplay** — no uncertainty, no sample size, huge font conclusion
2. **Axis crimes** — truncated axes that manufacture drama
3. **Time cherry-pick** — zoom to the winning window
4. **Metric laundering** — flashy secondary metric hides primary failure
5. **Baseline erasure** — model curve with no reference
6. **Legend fog** — unreadable encodings, 12 colors, no point
7. **Dual-axis trickery** — unrelated series forced into fake correlation
8. **Heatmap theater** — giant correlation mats with no hypothesis
9. **3D / pie distraction** for simple comparisons
10. **Screenshot science** — unreproducible UI grabs as proof
11. **Probabilities as destiny** — 53% shown like a lock
12. **Money curves without costs/assumptions**

## Procedure

1. Identify the intended claim of each visual.
2. Check encoding honesty (axes, scales, filters, missing baselines).
3. Check statistical honesty (n, period, uncertainty, selection).
4. Check claim alignment (does visual match earned claim level?).
5. Mark each visual:
   - `keep`
   - `fix`
   - `kill`
6. Rewrite titles/captions to state what was measured, not a sales line.
7. Prefer one clear visual over five decorative ones.
8. Emit a cleaned presentation plan.

## Replacement defaults

| Instead of | Prefer |
|---|---|
| Rainbow equity curve only | metric table + baseline deltas + period notes |
| Pie charts for model compare | dot/bar with shared baseline |
| Giant feature importance flex | top drivers + stability caveat |
| Smooth marketing gradient cards | plain tables with n and dates |
| “Insight” callout boxes | falsifiable sentence + limit |

## Hard constraints

- Never truncate axes to manufacture an effect without explicit warning (default: don’t)
- Never drop losing segments silently
- Never present in-sample curves as validation
- Never decorate a `kill`/`explore` result into paper/market clothing
- Every key figure needs: period, n (or event count), metric definition
- If uncertainty is unknown, say unknown — do not draw fake error bars

## Anti-patterns

- **Dashboard makeup** on a weak model
- **Annotation spam** that tells viewers what to feel
- **Color as argument**
- **One magical chart** carrying the whole claim
- **UI skins over missing method**

## Output contract

Done means:

- [ ] Each visual scored `keep` / `fix` / `kill`
- [ ] Specific slop issues named
- [ ] Replacement guidance given
- [ ] Caption/title rewrites provided where needed
- [ ] Claim-level alignment checked
- [ ] Remaining risk of misreading stated

## Handoffs

- `results-reporting` — final prose around cleaned visuals
- `calibration-check` — if reliability figures are needed
- `model-interpretation` — if driver plots are the point
- `model-card` — store canonical figures/limits
- **Stop** when presentation no longer outruns evidence

## Worked example

**Input:** chart titled “Dominant Edge” showing cumulative “units” from one season, y-axis starts at +10, no baseline, no close-line reference.

**Audit:**
- axis crime + cherry-pick + baseline erasure + overclaim title
- verdict: `kill` chart

**Replace with:**
- table of walk-forward log-loss vs baselines by season
- optional calibration note
- title: “Walk-forward log-loss vs baselines (2019–2024)”
- non-claim: not a profit proof

## References

- `skills/edge-writeup`
- `skills/ethics`
- `skills/doctrine`
- `skills/backtest-critique`
- Tufte-style chartjunk skepticism; baseline-first reporting
