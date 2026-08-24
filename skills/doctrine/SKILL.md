---
name: doctrine
description: >
  Define sports-analytic edge vs noise, rank evidence, and decide ship /
  paper-only / kill. Use when starting an analysis, judging whether a model
  claim is valid, setting success criteria, or deciding if work is done.
version: "0.1.0"
license: MIT
---

# Doctrine

Foundation skill for Sports Analytic Skills. This is the judgment layer:
what counts as good sports-modeling work, what evidence outranks what, and
when to stop.

## When to use

- Starting any sports modeling or analytics task
- A user asks “is this model good?”, “do we have edge?”, or “should we ship?”
- Before writing features, backtests, or market claims
- When results look good and need a kill/ship gate
- When an agent is about to treat fit metrics as proof

## When not to use

- Pure data plumbing with no claim about predictive quality
- Sport-rules trivia with no modeling decision
- Stake sizing language details → use `risk`
- Honesty/refusal/tip-shop boundaries → use `ethics`
- Concrete leakage walkthrough → use `leakage-audit` after doctrine framing

## Required inputs

Minimum:

- **Question:** what is being predicted or evaluated?
- **Claim level sought:** exploration / paper model / market-relative claim

Optional but important:

- Available data windows and grain (game, player-game, possession, etc.)
- Whether market/odds data exists
- Intended use (research, content, decision support)

If the question is vague, clarify before modeling.

## Core definitions

### Analytic edge (this library’s meaning)

A reusable process that, under a pre-registered validation design, produces
predictions or decisions that beat a relevant baseline out of sample, with
uncertainty honestly reported.

Edge is **not**:

- a high R² in-sample
- a leaderboard screenshot
- a story that fits last night’s game
- a complex model that has not beaten a dumb baseline

### Noise / non-edge

Patterns that disappear under time-safe validation, fail against baselines,
depend on leakage, or cannot be stated as a falsifiable claim.

### Evidence hierarchy (highest wins)

When evidence conflicts, rank roughly as:

1. Pre-registered / time-safe out-of-sample performance vs strong baselines
2. Market-relative evaluation (e.g. closing-line) **when market data exists**
3. Calibration and probability quality on unseen periods
4. Robustness across seasons/regimes/subsets agreed in advance
5. In-sample fit, feature importances, highlight charts

Pretty charts do not outrank weak out-of-sample evidence.

### Claim levels

| Level | Allowed when | Not allowed to say |
|---|---|---|
| `explore` | EDA, hypothesis generation | “this works”, “+EV” |
| `paper` | Time-safe validation vs baselines, no/insufficient market proof | “actionable market edge” |
| `market-relative` | Paper bar met **and** honest market evaluation supports it | guaranteed profit, locks |
| `kill` | Failed gates, leakage, or irreproducible claims | continued hype |

Default new work to `explore` or `paper` until evidence upgrades it.

## Procedure

1. **State the decision question**
   - Target variable
   - Decision the model would inform
   - Sport-agnostic form first (module constraints later)

2. **Name the baselines**
   - At least one strong simple baseline must exist before complexity
   - If no baseline is defined, stop and define one (`baseline-models`)

3. **Choose claim level sought**
   - `explore`, `paper`, or `market-relative`
   - If market data is absent, cap at `paper`

4. **Pre-commit validation design**
   - Time order, split method, embargo/gap if needed
   - Metrics that match the decision (not vanity metrics only)
   - Hand off to `validation-design` for mechanics

5. **Run work under constraints**
   - Features must be time-safe (`feature-rules`, `leakage-audit`)
   - No peeking at holdout to tune the story

6. **Score against the evidence hierarchy**
   - Did it beat baselines out of sample?
   - Is calibration acceptable for the claim level?
   - If market-relative claim: require market evaluation path (`clv-evaluation` when applicable)

7. **Issue a verdict**
   - `ship-paper` — valid as research/paper claim
   - `ship-market-relative` — only with market evidence
   - `revise` — specific failed gate
   - `kill` — fatally flawed or not worth more cycles

8. **Write the claim card**
   - One short paragraph: what is claimed, what is not claimed, evidence, limits
   - Hand off to `model-card` for fuller writeups

## Hard constraints

- Never treat in-sample fit as sufficient evidence of edge
- Never upgrade to market-relative claims without market-relative evidence
- Never skip baselines to celebrate a complex model
- Never change the validation design after seeing test results to “save” a narrative
- Never present exploration work as production-ready edge
- Always state the claim level in outputs
- Always prefer time-safe evaluation over random splits for sports chronologies
- If required evidence is missing, downgrade the claim — do not fill gaps with confidence

## Anti-patterns

- **Backtest theater:** beautiful equity curve, no pre-committed design
- **Baseline amnesia:** deep model with no comparison to mean/season average/Elo-like simple model
- **Metric shopping:** reporting only the metric that looked good
- **Regime blindness:** one hot season treated as universal law
- **Story first:** deciding the narrative, then finding supporting slices
- **Market cosplay:** saying “edge” when only offline accuracy exists
- **Complexity cosplay:** stacking models before a single well-validated simple model exists
- **Infinite revision:** tweaking until holdout cooperates

## Output contract

Done means the agent produced:

- [ ] Decision question and target, clearly stated
- [ ] Claim level sought and claim level earned
- [ ] Baselines named
- [ ] Validation design summary (or explicit handoff)
- [ ] Evidence reviewed in hierarchy order
- [ ] Verdict: `ship-paper` / `ship-market-relative` / `revise` / `kill`
- [ ] Non-claims listed (what this does **not** prove)
- [ ] Next handoff or stop condition

## Handoffs

- `ethics` — if the user wants picks, locks, guarantees, or overconfident public claims
- `risk` — uncertainty language, calibration framing, stake discipline wording
- `baseline-models` — no baseline defined
- `feature-rules` / `leakage-audit` — feature integrity
- `validation-design` — split/walk-forward mechanics
- `backtest-critique` — reviewing an existing claimed system
- `clv-evaluation` / `calibration-check` — when claim level needs market or prob quality evidence
- `model-card` / `experiment-log` — documentation of the result
- **Stop** if verdict is `kill` and no new data/design is proposed

## Worked example

**Request:** “Build a model that predicts whether the home team wins. Looks great — 68% accuracy.”

**Doctrine pass:**

1. Question: P(home win) before tipoff/start.
2. Baselines required: home-win base rate; simple rating differential model.
3. Claim sought: user said “great” → they want at least `paper`; market-relative not yet earned.
4. Checks:
   - Was accuracy computed with time-safe splits?
   - Does it beat home base rate and simple ratings on future seasons?
   - Any post-start features (in-game score, delayed injury status)?
5. Suppose accuracy is in-sample only and equals home base rate in walk-forward.
6. Verdict: `kill` as edge; allowed as `explore` demo only.
7. Non-claim: this does not support betting language or “model works” public claims.

## References

- Repo architecture: `ARCHITECTURE.md`
- Authoring boundaries: `docs/skill-authoring.md`
- Related concepts: model cards, walk-forward validation, baseline-first modeling
- Market evaluation is optional evidence, not a substitute for time-safe validation
