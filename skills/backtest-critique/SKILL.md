---
name: backtest-critique
description: >
  Tear apart a claimed sports-model backtest. Use when reviewing performance
  reports, equity-style curves, notebook results, or any “this model works”
  claim that needs an adversarial audit.
version: "0.1.0"
license: MIT
---

# Backtest Critique

Adversarial review skill for claimed sports-model performance. Assume the
backtest is overstated until it survives doctrine, leakage, baselines, and
validation checks.

## When to use

- User presents a backtest, ROI curve, or “model hit rate”
- README/notebook claims look too clean
- Choosing whether a historical result is publishable as paper evidence
- Post-mortem on a failed or suspicious system

## When not to use

- Designing validation before any results exist → `validation-design`
- Building features from scratch → `feature-rules`
- Writing public hype copy → `ethics` (likely refuse)
- Pure market CLV math with no model backtest → `clv-evaluation`

## Required inputs

Minimum:

- Claimed result (metrics, period, target)
- Model/process description
- Validation method used (or admission that none exists)

Optional:

- Code/notebook
- Feature list
- Baseline comparisons
- Market/odds data availability

## Critique checklist

1. **Claim clarity**
   - What exactly is claimed?
   - Pre-event or not?
   - Paper vs market-relative language?

2. **Baseline presence**
   - Are Tier A/B baselines reported on the same split?
   - If no → major fail

3. **Validation integrity**
   - Walk-forward / time order?
   - Random K-fold on events?
   - Holdout peeking / repeated final-season tourism?

4. **Leakage surface**
   - Same-event stats?
   - as-of joins?
   - Target encodings?
   - Market close used at open time?

5. **Metric honesty**
   - Primary metric chosen before results?
   - Probabilistic metrics for probability models?
   - Hidden vig/costs if money curve shown?

6. **Stability**
   - Multiple seasons/regimes?
   - One hot slice driving everything?
   - Performance decay over time?

7. **Sample size**
   - Enough events for the claim intensity?
   - Error bars / uncertainty mentioned?

8. **Reproducibility**
   - Can an independent agent rerun this?
   - Seeds, versions, data cuts documented?

## Procedure

1. Restate the claim in one hard sentence.
2. Map claim level under `doctrine` (`explore` / `paper` / `market-relative` / `kill`).
3. Run checklist above; mark each item `pass` / `fail` / `unknown`.
4. Pull in specialized skills as needed:
   - `leakage-audit`
   - `baseline-models`
   - `validation-design`
   - `clv-evaluation` if market claims exist
5. Issue critique verdict:

| Verdict | Meaning |
|---|---|
| `stands-paper` | Credible paper evidence under stated limits |
| `stands-market-relative` | Credible only if market evidence also passes |
| `weak` | Some signal possible; overclaimed or fragile |
| `does-not-stand` | Fails integrity/baseline/validation bars |
| `invalid` | Contaminated or nonsensical evaluation |

6. List the minimum repairs required before any stronger claim.
7. Hand rewritten allowed claim text to `ethics` standards.

## Hard constraints

- Never accept a money curve as proof without method integrity
- Never upgrade a weak offline backtest to market edge language
- Never ignore missing baselines
- Never treat unknown methodology as neutral; treat as risk
- If critical checklist items are `unknown`, cap verdict at `weak` or below

## Anti-patterns

- **Curve worship**
- **Single-metric storytelling**
- **“It worked on my notebook” reproducibility**
- **Silent row filters that remove losses**
- **Post-hoc rule changes after seeing results**
- **Using future news labels in historical picks**

## Output contract

Done means:

- [ ] Claim restated
- [ ] Checklist scored
- [ ] Verdict issued
- [ ] Top failure reasons ranked
- [ ] Allowed rewritten claim (or refuse)
- [ ] Repair list before stronger claims
- [ ] Handoffs identified

## Handoffs

- `leakage-audit` / `validation-design` / `baseline-models` for repairs
- `doctrine` for final ship/kill
- `ethics` for communication limits
- `model-card` to document surviving claims
- `clv-evaluation` if market-relative claim is in play
- **Stop** on `invalid` until rebuilt

## Worked example

**Claim:** “From 2019–2024 our model is 58% ATS with steady profit.”

Critique sketch:

1. Claim is market-action shaped → needs market-relative bar.
2. No baseline ATS source / closing-line reference provided → fail.
3. Split method unknown → fail.
4. Feature timing unknown → suspect leakage.
5. Verdict: `does-not-stand`.
6. Allowed rewrite: none for profit claim; invite full charter + leakage audit + CLV.

## References

- `skills/doctrine`
- `skills/leakage-audit`
- `skills/baseline-models`
- `skills/validation-design`
- `skills/ethics`
