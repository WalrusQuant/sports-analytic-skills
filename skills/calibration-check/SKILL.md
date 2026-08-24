---
name: calibration-check
description: >
  Measure whether sports-model probabilities mean what they say. Use when
  evaluating probability quality, reliability curves, or probabilistic
  prediction models.
version: "0.1.0"
license: MIT
---

# Calibration Check

Market/modeling joint skill for probability reliability. A model can rank
well and still be miscalibrated. This skill checks whether 30% means ~30%.

## When to use

- Model outputs probabilities
- User asks how confident / how sure
- Before `risk` stake-discipline language stronger than research-only
- Supporting `paper` or `market-relative` probabilistic claims
- Comparing recalibration methods

## When not to use

- Pure ranking tasks with no probabilistic interpretation
- Hard labels only with no prob outputs
- Ethics refusals for locks → `ethics`
- Designing splits → `validation-design`

## Required inputs

Minimum:

- Predicted probabilities on a time-safe evaluation set
- Binary (or properly binned) outcomes
- Validation fold IDs / timestamps

Optional:

- Market-implied probabilities for comparison
- Desired probability bins
- Segment keys (season, home/away, sport if multi-sport panel)

## What to measure

1. **Reliability / calibration curve**
2. **Expected Calibration Error (ECE) or similar**
3. **Brier score decomposition** (reliability vs resolution) when useful
4. **Segment calibration** (not only pooled)
5. **Sharpness** (are probs informative, not all 0.5?)

Discrimination metrics (AUC/log-loss) can be reported, but they do not replace calibration.

## Procedure

1. Confirm evaluation predictions are from forward/time-safe folds.
2. Clip/validate probability range in (0,1) with no NaNs.
3. Choose binning strategy (fixed bins or quantile bins); pre-declare it.
4. Compute calibration curve + summary error.
5. Compute Brier and, if possible, reliability/resolution components.
6. Slice by season/regime; look for fragile calibration.
7. Optional: compare to market-implied calibration if odds exist.
8. Decide whether recalibration is allowed:
   - only using training/forward-proper methods
   - never fit isotonic on final holdout and call it validated without nested design
9. Issue calibration verdict:

| Verdict | Meaning |
|---|---|
| `well-calibrated` | Reliability acceptable for claim level |
| `usable-with-caveats` | Some miscalibration; disclose and/or recalibrate properly |
| `poorly-calibrated` | Prob numbers not trustworthy as probabilities |
| `invalid-eval` | Leakage/split issues block judgment |

10. Hand posture to `risk` and claim impact to `doctrine`.

## Hard constraints

- Never evaluate calibration on training rows used to fit the same model without nested scheme disclosure
- Never present raw scores as probabilities without calibration evidence
- Never fix calibration by peeking at final test labels
- Never hide segment failures behind a pooled “looks fine”
- If sample per bin is tiny, say so and widen bins or reduce claim strength

## Anti-patterns

- **Accuracy cosplay:** “56% correct, so calibrated”
- **One reliability plot, no sample sizes**
- **Holdout isotonic theater**
- **Average prob ≈ base rate therefore calibrated** (necessary, not sufficient)
- **Ignoring 0.05 and 0.95 tails where decisions often live**

## Output contract

Done means:

- [ ] Eval set time-safety confirmed
- [ ] Calibration method/binning stated
- [ ] Summary calibration metric reported
- [ ] Curve/table with bin counts
- [ ] Segment notes
- [ ] Verdict issued
- [ ] Implications for claim level and stake language

## Handoffs

- `risk` — posture after calibration verdict
- `doctrine` — claim level impact
- `clv-evaluation` — if market probs available
- `validation-design` — if eval design is insufficient
- `model-card` — document calibration status
- **Stop** on `invalid-eval` until redesign

## Worked example

**Model:** pre-event home win probabilities.  
**Walk-forward bins:** 10 equal-width bins.  
**Finding:** predictions around 0.70 win only ~0.60 over 3 seasons; tails overconfident.  
**Verdict:** `poorly-calibrated` for strong confidence language.  
**Actions:** proper nested recalibration experiment; until then `risk` posture `research-only` / `cautious`; no market-action wording.

## References

- `skills/risk`
- `skills/doctrine`
- `skills/validation-design`
- `skills/clv-evaluation`
