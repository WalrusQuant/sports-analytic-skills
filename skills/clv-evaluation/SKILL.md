---
name: clv-evaluation
description: >
  Evaluate sports predictions with closing-line / market-relative metrics.
  Use when odds exist and a model or process claims market relevance, value,
  or more than paper accuracy.
version: "0.1.0"
license: MIT
---

# CLV Evaluation

Market-layer skill for market-relative evaluation. Closing-line value and
related checks are how paper models get stress-tested against the market.

## When to use

- Model claims “value,” “edge,” or market usefulness
- User has open/close lines and predictions/decisions
- Deciding whether claim level may rise to `market-relative`
- Comparing processes beyond offline accuracy

## When not to use

- No trustworthy odds panel → stay paper-only (`doctrine`)
- Odds panel not cleaned → `market-data-hygiene` first
- Pure offline baseline comparison with no market claim
- Request for picks/locks → `ethics` refuse path

## Required inputs

Minimum:

- Clean-enough odds panel with defined close
- Predictions or decisions timestamped at/before decision time Td
- Event outcomes (for complementary diagnostics)

Optional:

- Multiple books
- Stake notionals (for cost-aware diagnostics only)
- Open lines for open-to-close context

## Core metrics (choose those that fit the market type)

### Always-on diagnostics

- Coverage: fraction of events with valid close at Td
- Latency honesty: prediction time vs close time

### CLV-style

For price-taking decisions or probability comparisons:

- Closing line value versus the bet/price at Td
- Predicted probability vs close-implied probability (vig-adjusted if possible)
- Sign consistency: did model side beat close on average?

### Outcome-linked (secondary)

- Calibration by market-implied buckets
- ROI-like diagnostics only with explicit cost assumptions and never alone

## Procedure

1. Confirm odds panel status from `market-data-hygiene`.
2. Freeze decision timestamp Td (<= event start; usually <= close definition).
3. Align each prediction/decision to a close quote.
4. Vig-adjust implied probabilities when comparing probs.
5. Compute primary market-relative metrics on all eligible events.
6. Slice by season/regime/book if available (pre-registered slices preferred).
7. Compare against naive market baselines (e.g. always open line, always favorite).
8. Interpret with uncertainty:
   - small samples do not unlock big claims
9. Issue market verdict:

| Verdict | Meaning |
|---|---|
| `market-supportive` | Stable positive market-relative evidence |
| `market-neutral` | No reliable market advantage shown |
| `market-hostile` | Evidence against usefulness vs close |
| `invalid-market-eval` | Data/method too weak to judge |

10. Feed verdict into `doctrine` claim-level decision.

## Hard constraints

- Never claim market edge from offline accuracy alone
- Never compute CLV with post-start closes
- Never hide vig when it changes the conclusion
- Never use only winning weeks/books
- If coverage is low, state it and cap confidence
- ROI stories cannot override negative/neutral CLV without extraordinary evidence

## Anti-patterns

- **Close leakage:** using close as a feature then celebrating CLV
- **Book shopping after the fact**
- **Open-only fantasy** with no close reference when close exists
- **Tiny-sample CLV heroics**
- **Probability vs moneyline mismatch** without conversion discipline

## Output contract

Done means:

- [ ] Td and close definition stated
- [ ] Coverage reported
- [ ] Primary CLV/market metrics reported
- [ ] Slices/baselines reported or explicitly unavailable
- [ ] Verdict issued
- [ ] Claim-level implication stated
- [ ] Limits listed (books, sample, vig handling)

## Handoffs

- `market-data-hygiene` if panel fails
- `calibration-check` for probability reliability vs outcomes
- `doctrine` for claim upgrade/downgrade
- `backtest-critique` when market metrics are part of a broader claim audit
- `ethics` before any public market-edge language
- **Stop** on `invalid-market-eval` until data fixes

## Worked example

**Setup:** pre-game win probs at Td = 60 minutes before start; close = last quote <= start.  
**Result:** mean model-prob edge vs vig-adjusted close ≈ 0 across 4 seasons; mild positive one season only.  
**Verdict:** `market-neutral`.  
**Doctrine implication:** remain `paper` at best; no market-relative upgrade.

## References

- `skills/market-data-hygiene`
- `skills/doctrine`
- `skills/calibration-check`
- `skills/ethics`
