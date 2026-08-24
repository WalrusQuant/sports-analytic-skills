---
name: baseline-models
description: >
  Define and beat strong simple baselines before complex sports models.
  Use when starting a modeling project, choosing reference models, or
  checking whether a fancy model is actually earning its complexity.
version: "0.1.0"
license: MIT
---

# Baseline Models

Modeling-spine skill. No complex sports model is allowed to claim value
until it beats relevant simple baselines under the same validation design.

## When to use

- Starting a new predictive sports-modeling task
- User jumps straight to ML/deep models
- Reviewing a model with no reference comparisons
- Deciding whether complexity is justified
- Setting the minimum bar for `doctrine` paper claims

## When not to use

- Pure EDA with no predictive claim
- Leakage inspection of an existing feature set → `leakage-audit`
- Designing walk-forward mechanics → `validation-design`
- Market-only evaluation with no model comparison → market skills

## Required inputs

Minimum:

- Prediction target (binary event, margin, total, rank, count, etc.)
- Decision grain (game, player-game, team-season, possession, etc.)
- Available historical window

Optional:

- Existing candidate model
- Known strong domain baselines
- Metric preferences tied to the decision

## Baseline tiers

Build from lower to higher. A candidate model must beat the strongest
applicable baseline tier you can implement honestly.

### Tier A — Naive / null

Examples (sport-agnostic forms):

- Global base rate / mean / median
- Home/away stratified base rate when that split is known pre-event
- Season-to-date mean with time-safe availability
- Last-value / moving average where appropriate

### Tier B — Simple structural

Examples:

- Linear / logistic model on a few pre-event ratings or form features
- Elo-like or strength-difference baseline
- Poisson/negbin mean model for counts
- Opponent-adjusted average where computable without leakage

### Tier C — Strong classical

Examples:

- Regularized linear models with a small curated feature set
- Gradient-boosted trees only after A/B exist as references
- Simple ensembles of strong simples (not stack-of-stacks first)

Rule: **Tier C is not a free pass.** It still must beat A/B on time-safe validation.

## Procedure

1. **Freeze the target and prediction time**
   - What is predicted?
   - At what timestamp must all inputs be known?

2. **Choose metrics that match the decision**
   - Classification: log-loss / Brier first; accuracy secondary
   - Continuous: MAE/RMSE plus bias checks
   - Ranking: appropriate ranking loss if rank is the product
   - Do not optimize only vanity accuracy

3. **Implement Tier A baselines**
   - Document formulas
   - Ensure time-safe computation (no future data)

4. **Implement at least one Tier B baseline**
   - Prefer interpretable strength/form models
   - Same splits/metrics as candidate

5. **Only then train the candidate model**
   - Same features availability timestamp
   - Same validation scheme (`validation-design`)

6. **Compare on the held-out / walk-forward windows**
   - Absolute metric deltas
   - Stability across seasons/regimes
   - Calibration if probabilities are produced (`risk` / `calibration-check`)

7. **Complexity verdict**

| Result | Verdict |
|---|---|
| Candidate loses to A or B | `reject-complexity` |
| Ties within noise | `not-earned` |
| Beats B honestly and stably | `complexity-justified` |
| Beats B only in-sample | `invalid-comparison` |

8. **Record baseline card**
   - Baseline definitions
   - Metrics
   - Windows
   - Verdict

## Hard constraints

- Never evaluate a complex model without at least Tier A and one Tier B baseline
- Never compare models on different splits or different row filters
- Never tune baselines on the final test window after candidate tuning
- Never report only the metric that favors the candidate
- Never use future-knowing baselines (final standings, post-event restatements)
- If baseline data is unavailable, downgrade claim level instead of skipping baselines quietly

## Anti-patterns

- **Deep learning first**
- **Baseline as strawman:** intentionally weak null to make ML look good
- **Train-test contamination in baseline stats**
- **One-season miracle comparisons**
- **Metric laundering:** switch metrics after seeing results
- **Feature mismatch:** candidate gets extra leaked fields baselines never had
- **Ensemble theater:** stacking weak models instead of improving the baseline

## Output contract

Done means:

- [ ] Target + prediction timestamp defined
- [ ] Metrics justified
- [ ] Tier A baseline implemented/documented
- [ ] Tier B baseline implemented/documented
- [ ] Candidate compared on the same validation design
- [ ] Complexity verdict issued
- [ ] What must improve before more complexity is allowed

## Handoffs

- `doctrine` — claim level update after baseline results
- `feature-rules` — build cleaner simple features for Tier B/C
- `validation-design` — formalize splits/walk-forward
- `leakage-audit` — if baseline or candidate may be time-contaminated
- `backtest-critique` — reviewing an existing no-baseline system
- `model-card` — persist baseline comparisons
- **Stop** on `reject-complexity` unless a new design/data plan exists

## Worked example

**Request:** “Train XGBoost to predict home win probability.”

1. Target: home win; prediction time = scheduled start.
2. Metrics: log-loss + Brier; accuracy secondary.
3. Tier A: home win base rate by season-to-date (time-safe).
4. Tier B: logistic model on pre-event rating difference + rest indicator.
5. Candidate: XGBoost on expanded pre-event features.
6. Walk-forward result (illustrative): XGBoost log-loss worse than Tier B.
7. Verdict: `reject-complexity`. Keep/improve Tier B; do not ship XGBoost as progress.

## References

- Doctrine baselines requirement: `skills/doctrine`
- Validation mechanics: `skills/validation-design`
- Feature timing: `skills/feature-rules`
