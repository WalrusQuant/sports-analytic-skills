---
name: leakage-audit
description: >
  Audit sports-modeling pipelines for look-ahead and target leakage. Use when
  reviewing features, joins, labels, splits, or any “too good” backtest that
  may have seen the future.
version: "0.1.0"
license: MIT
---

# Leakage Audit

Adversarial modeling-spine skill. Assume leakage until the pipeline proves
time-safe. This skill tears apart feature/label/split contamination.

## When to use

- Any finished or draft feature matrix before claiming performance
- Backtests that look suspiciously strong
- Reviewing joins across schedule, box score, injury, and odds tables
- User says “just quick model” with rich historical tables
- After `feature-rules` as a second-pass audit

## When not to use

- Brand-new problem with no pipeline yet → start with `feature-rules`
- Market CLV evaluation specifics → `clv-evaluation`
- Ethics of overclaiming results → `ethics` after audit verdict
- Sport trivia without a data pipeline

## Required inputs

Minimum:

- Declared prediction timestamp rule T
- Target definition
- Feature list / pipeline code / SQL
- Split or walk-forward method

Optional:

- Row-level sample
- Source refresh delays
- Reported metrics that seem too good

## Leakage classes

1. **Target leakage** — feature contains outcome information
2. **Look-ahead leakage** — feature uses data from t > T
3. **Split leakage** — train/test not isolated (same event, player-game clones, random shuffle on time series)
4. **Aggregation leakage** — group stats computed with future or current row
5. **Label leakage** — label redefined using future knowledge
6. **Market leakage** — using closes/post lines for open-time decisions
7. **Leakage by correction** — restated stats treated as live-available

## Procedure

1. **Restate T and label timing**
   - When is the prediction made?
   - When does the label become known?

2. **Map every input field to a known-time**
   - `known_by <= T` required for legal training/inference inputs

3. **Inspect joins**
   - Keys only, or keys + time?
   - as-of merges vs exact event ID merges that pull same-game stats

4. **Inspect aggregates**
   - Expanding/rolling windows end index
   - Groupby target means
   - Season stats computation order

5. **Inspect splits**
   - Random K-fold on chronological sports events = fail by default
   - Adjacent-event leakage across train/test without embargo
   - Duplicate entities on both sides

6. **Run red-flag checks**
   - Near-perfect AUC/R² on hard tasks
   - Single feature dominates with post-event meaning
   - Performance collapses when shifting features by +1 event
   - Shuffle-of-time destroys or does not destroy performance unexpectedly

7. **Assign audit verdict**

| Verdict | Meaning |
|---|---|
| `clean` | No material leakage found under stated assumptions |
| `suspect` | Timing ambiguities remain; claim capped |
| `contaminated` | Confirmed leakage path |
| `fatal` | Core label/feature design is invalid |

8. **Prescribe fixes**
   - Drop fields, shift timestamps, embargo splits, rebuild aggregates
   - Require re-validation from scratch after fixes

## Hard constraints

- Never clear a pipeline that uses random splits on time-ordered sports events without explicit justification
- Never accept same-event box-score features for pre-event claims
- Never accept target encodings fit on the full shuffled dataset
- Never accept “probably fine” without a known-time map
- If audit is blocked by missing timestamps, verdict is at best `suspect`
- Contaminated pipelines cannot support `paper` or `market-relative` claims until rebuilt

## Anti-patterns

- **Metric denial:** “but CV score is high, so leakage is okay”
- **One-column blindness:** checking features, ignoring label construction
- **Notebook order tricks:** cells re-run out of order creating hidden state leakage
- **ID merge comfort:** assuming event IDs make time safety automatic
- **Partial purge:** dropping one leaked column, leaving leaked aggregates
- **Test peeking:** using test performance to choose which leakage to ignore

## Output contract

Done means:

- [ ] T and label-time restated
- [ ] Known-time map for key fields
- [ ] Leakage classes checked
- [ ] Verdict: `clean` / `suspect` / `contaminated` / `fatal`
- [ ] Concrete failure paths listed (if any)
- [ ] Required fixes listed
- [ ] Claim-level implication stated (`explore` only, rebuild, etc.)

## Handoffs

- `feature-rules` — rebuild legal features
- `validation-design` — fix split/embargo design
- `backtest-critique` — full claim teardown including leakage findings
- `doctrine` — downgrade/kill claim level
- `ethics` — block overclaim language on contaminated work
- **Stop** after `fatal` until redesign

## Worked example

**Request:** “Model predicts player points at 0.95 R² using team total and player minutes.”

1. T claimed: pre-tip.
2. Features: player minutes, team total points.
3. Audit:
   - minutes and team total are same-event outcomes for pre-tip T
   - target leakage + look-ahead
4. Verdict: `fatal` for pre-tip claim.
5. Fix paths:
   - either predict pre-tip with prior-event features only
   - or change task to in-game projection with in-game T and only then-available live stats

## References

- Feature legality: `skills/feature-rules`
- Splits: `skills/validation-design`
- Claim impact: `skills/doctrine`
