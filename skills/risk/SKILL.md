---
name: risk
description: >
  Frame uncertainty, calibration, and stake discipline for sports models.
  Use when discussing probability quality, confidence, bankroll language,
  ruin awareness, or whether a result is stable enough to act on.
version: "0.1.0"
license: MIT
---

# Risk

Uncertainty and discipline skill for Sports Analytic Skills. This skill
governs **how uncertain results are described** and **how stake language
may be framed**. It is not a bankroll product and not betting advice.

## When to use

- Model outputs probabilities and someone asks “how sure?”
- Need calibration / sharpness framing
- User starts talking units, Kelly, bankroll, or bet size
- Evaluating whether a paper edge is fragile
- Stressing regime shift, sample size, or ruin risk

## When not to use

- Deciding if evidence beats baselines → `doctrine`
- Refusal of locks/guarantees → `ethics`
- Implementing full portfolio software / accounting tools
- Detailed market microstructure without odds context → market skills

## Required inputs

Minimum:

- The predictive claim and claim level (`explore` / `paper` / `market-relative`)
- How uncertainty is represented (probability, score, rank, point spread, etc.)

Optional:

- Sample size / number of events in evaluation window
- Calibration plots or probability reliability stats
- Whether odds/limits/fees exist in the problem
- User’s stake language request (units, % bankroll, Kelly, etc.)

## Core ideas

### Uncertainty is part of the model

A point prediction without uncertainty handling is incomplete for decision talk.

### Calibration before swagger

If events called ~30% do not happen near 30% long-run (in appropriate buckets),
confidence language must be reduced or the model revised.

### Stake language is optional and capped

This skill may discuss **discipline framing** (caps, unit risk, no martingale).
It does not:

- manage someone’s money
- promise growth
- prescribe a personal betting plan as advice

### Fragility checks matter

Small samples, one season wonders, rule changes, and structural breaks can
erase apparent edges. Risk framing must say so.

## Procedure

1. **Identify the uncertainty object**
   - Probability of binary event
   - Expected value distribution
   - Rank/order forecast
   - Margin/total continuous forecast

2. **Check representation quality**
   - Are probabilities actual probabilities or arbitrary scores?
   - If scores, do not fake percent confidence
   - If probabilities, ask for calibration evidence when claim level > explore

3. **Sample-size and variance sanity**
   - Tiny event counts → wide uncertainty, no bold stake talk
   - Hot streak windows are not risk proof

4. **Calibration framing**
   - Prefer reliability over a single accuracy number
   - Separate discrimination (“ranks well”) from calibration (“rates mean what they say”)
   - Hand off deep measurement to `calibration-check` when available

5. **Regime / break awareness**
   - Rule changes, roster construction eras, scheduling changes, inflation of pace, etc.
   - Ask whether evaluation spans more than one regime

6. **Stake-discipline framing (only if user asks or claim is decision-facing)**
   - Default: small fixed fraction / unit risk thinking
   - No martingale / chase language
   - No “all-in on edge” language
   - Kelly, if mentioned, is an upper-bound concept and usually too aggressive raw
   - Always pair stake talk with: uncertainty, limits, and possible model death

7. **Issue risk posture**

| Posture | Meaning |
|---|---|
| `research-only` | No stake language appropriate |
| `cautious` | Small hypothetical units at most; high uncertainty |
| `standard-discipline` | Normal unit discipline framing allowed with disclosures |
| `reduce-or-stop` | Evidence fragile, degraded, or broken |

8. **Write the uncertainty paragraph**
   - What is uncertain
   - What would falsify the claim
   - What stake language is/isn’t justified

## Hard constraints

- Never present uncalibrated scores as precise probabilities
- Never use martingale / chase-loss stake logic
- Never imply bankroll growth is assured
- Never give personalized financial/betting advice
- Never size up because recent hits “feel hot”
- Never ignore vig, limits, or execution constraints when stake language is used with markets
- If sample is tiny, force `research-only` or `cautious`
- If claim level is `explore` or `kill`, no stake language

## Anti-patterns

- **False precision:** 51.238% spoken like destiny
- **Kelly cosplay:** full Kelly on a half-validated model
- **Unit fiction:** “1% bankroll forever” with no drawdown discussion
- **Independence fantasy:** correlated bets treated as independent coin flips
- **No-death fantasy:** model assumed permanently alive
- **Calibration skip:** accuracy reported, reliability ignored
- **Risk theater:** long jargon with no plain-language limit
- **Revenge sizing:** increasing risk after losses

## Output contract

Done means:

- [ ] Uncertainty object identified
- [ ] Risk posture assigned (`research-only` / `cautious` / `standard-discipline` / `reduce-or-stop`)
- [ ] Calibration/sample-size caveats stated
- [ ] Stake language either disciplined or explicitly declined
- [ ] Falsification condition stated (what would kill confidence)
- [ ] No guarantee / no chase / no personalized advice language

## Suggested language patterns

**Good**

- “Estimated probability; calibration checked on seasons A–C.”
- “Paper edge only; stake talk not justified without market-relative evidence.”
- “If used hypothetically, keep unit size small and predefine stop conditions.”
- “This can die under rule change / regime shift; revalidate each season.”

**Bad**

- “Lock this at 2% bankroll.”
- “Kelly says load the boat.”
- “We’ve hit 8 straight, increase size.”
- “Risk-free after hedging narrative.”

## Handoffs

- `doctrine` — claim level unclear or evidence incomplete
- `ethics` — user wants guarantees or pick authority
- `calibration-check` — formal probability reliability work
- `clv-evaluation` — market-relative performance and stability
- `validation-design` — need more robust evaluation under shifts
- `model-card` — persistent uncertainty/limits section
- **Stop** if posture is `reduce-or-stop` and no new validation is proposed

## Worked example

**Request:** “Model is 56% on an underdog. How many units?”

1. Uncertainty object: binary win probability.
2. Ask/claim checks:
   - Is 56% calibrated or a raw score?
   - Claim level? If only in-sample accuracy → `research-only`.
3. Suppose walk-forward exists but no calibration and no market evaluation.
4. Risk posture: `cautious` at best; prefer `research-only` for stake action.
5. Output:
   - Decline personal unit prescription as advice
   - Explain need for calibration + market-relative evidence
   - If hypothetical framing is insisted on: small fixed units, precommitted cap, stop rules, model-death clause
   - No “load up” language

## References

- Doctrine claim levels: `skills/doctrine`
- Ethics boundaries: `skills/ethics`
- Later measurement skill: `calibration-check`
- General concepts: probability calibration, bankroll drawdown, model risk, regime shift
