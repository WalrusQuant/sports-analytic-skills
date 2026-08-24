---
name: model-card
description: >
  Write an honest model/claim card for a sports model: intended use, data,
  validation, limits, and non-claims. Use when documenting a model, preparing
  a README section, or freezing what a model is allowed to say.
version: "0.1.0"
license: MIT
---

# Model Card

Documentation skill for sports models and analytic claims. The card is a
contract: what the model is, how it was tested, and what it must not claim.

## When to use

- After a model reaches a stable evaluation
- Before sharing results publicly or across teammates/agents
- When claim language keeps drifting stronger than evidence
- Packaging baselines + candidate comparison for the record

## When not to use

- No model/process exists yet
- Still in contaminated/exploratory mode with no evaluation charter
- User wants marketing blurbs instead of limits → `ethics`

## Required inputs

- Model/process name and version
- Target and prediction timestamp T
- Data window and sources
- Validation charter summary
- Baseline comparison summary
- Claim level earned (`explore` / `paper` / `market-relative` / `kill`)

## Card template

Fill every section. Use `unknown` explicitly rather than omitting.

1. **Identity**
   - Name / version / owners
   - One-sentence purpose

2. **Intended use**
   - In-scope tasks
   - Out-of-scope tasks

3. **Target and timing**
   - Label definition
   - Prediction timestamp rule T

4. **Data**
   - Sources
   - Grain
   - Windows
   - Known quality issues

5. **Features**
   - Summary of inputs
   - Legality stance / audit status

6. **Baselines**
   - Tier A/B references
   - Metrics deltas

7. **Validation**
   - Split scheme
   - Metrics
   - Regime slices
   - Tuning rules

8. **Results**
   - Forward performance summary
   - Calibration notes if probabilistic
   - Market-relative results if any

9. **Claim level**
   - Earned level
   - Allowed statements
   - Banned statements

10. **Limits and failure modes**
    - Sample size
    - Regime breaks
    - Known blind spots

11. **Ethics / advice posture**
    - Not-advice statement
    - No-lock / no-guarantee statement

12. **Maintenance**
    - Retrain cadence
    - Kill conditions
    - Monitoring signals

## Procedure

1. Gather evidence from `doctrine`, `baseline-models`, `validation-design`, audits.
2. Draft the card with the template.
3. Remove any sentence not supported by evidence.
4. Run an `ethics` pass on allowed/banned statements.
5. Add kill conditions (`risk` + `doctrine`).
6. Freeze version and link to `experiment-log` entries.

## Hard constraints

- Never leave limits section empty
- Never imply market edge from paper-only results
- Never omit baselines if performance is reported
- Never use lock/guarantee language
- If audit status is `suspect` or worse, claim level cannot be `paper`+ without repair notes

## Anti-patterns

- **Resume card:** only strengths, no limits
- **Metric dump without method**
- **Versionless myth model**
- **Copy-paste hype abstract**
- **Hidden data filters**

## Output contract

Done means:

- [ ] All 12 sections present
- [ ] Claim level explicit
- [ ] Allowed and banned statements listed
- [ ] Baselines + validation summarized
- [ ] Limits and kill conditions written
- [ ] Linked experiment references (or marked none)

## Handoffs

- `experiment-log` — store/version the evaluation run
- `ethics` — public wording review
- `edge-writeup` — human-facing summary later
- `backtest-critique` — if card exposes weak evidence
- **Stop** when card is frozen for this version

## Worked example

**Identity:** `home_win_logit_v3`  
**Purpose:** Estimate pre-start P(home win) from rating differential and rest.  
**Claim level:** `paper`  
**Allowed:** “Walk-forward log-loss beat season base rate and Elo-like baseline over seasons 2018–2024.”  
**Banned:** “Beats the market,” “bet this tonight,” “guaranteed value.”  
**Kill conditions:** two consecutive seasons failing baseline log-loss; major rule/regime break without revalidation.

## References

- `skills/doctrine`
- `skills/ethics`
- `skills/baseline-models`
- `skills/validation-design`
- `skills/experiment-log`
