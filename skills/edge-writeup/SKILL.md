---
name: edge-writeup
description: >
  Write an honest public or shared summary of a sports-modeling result:
  what was tested, what earned, limits, and non-claims. Use for README
  blurbs, post drafts, research notes, or stakeholder summaries.
version: "0.1.0"
license: MIT
---

# Edge Writeup

Comms skill for turning validated sports-modeling work into clear, honest
prose. This is not a hype engine. It translates claim level into language
a stranger can trust.

## When to use

- Summarizing a finished experiment or model version
- Drafting GitHub README result sections
- Drafting X/blog/research notes about a method (not picks)
- Converting a `model-card` into human-readable form
- User asks “explain what we found” after evaluation

## When not to use

- No evidence yet / only vibes
- User wants locks, picks, or guaranteed profit → `ethics` refuse
- Full formal contract doc → `model-card`
- Chart/presentation cleanup only → `anti-slop-analytics`
- Still-contaminated pipeline → fix with audit skills first

## Required inputs

Minimum:

- Claim level earned (`explore` / `paper` / `market-relative` / `kill`)
- Target + prediction timestamp T
- Validation summary
- Baseline comparison summary
- Limits / failure modes

Optional:

- CLV / calibration results
- Experiment IDs
- Audience (technical peers, general public, future self)

If claim level is unknown, run `doctrine` first.

## Writeup structure (default)

1. **One-line finding** (claim-level accurate)
2. **Question and setup**
3. **Data and timing**
4. **Baselines and method**
5. **Validation**
6. **Results that matter**
7. **What this does not show**
8. **Limits / kill conditions**
9. **Next test** (one concrete next step, or none)
10. **Not-advice line** when audience is public/decision-adjacent

## Language by claim level

| Level | Lead with | Avoid |
|---|---|---|
| `explore` | hypothesis, preliminary pattern | works, edge, beat the market |
| `paper` | out-of-sample vs baselines, method limits | locks, guaranteed +EV, actionable bet advice |
| `market-relative` | market-relative evidence + uncertainty | certainty, permanent edge, get-rich framing |
| `kill` | failed gate, do not use as edge | salvage hype, “almost works” cosplay |

## Procedure

1. Pull facts from `model-card` / `experiment-log` / critique outputs.
2. State audience and claim level.
3. Draft using the default structure.
4. Quantify only what was measured; mark absences as absences.
5. Put non-claims in their own section (not a footnote apology).
6. Run `ethics` pass: strip locks/guarantees/advice-shaped lines.
7. Run `anti-slop-analytics` if charts/tables are included.
8. Final check: could a hostile reviewer say you overclaimed? If yes, rewrite.

## Hard constraints

- Never outrun the earned claim level
- Never hide missing baselines, leakage status, or sample-size pain
- Never present exploration as production edge
- Never use tip-shop vocabulary
- Never imply the software places bets or manages money
- Public writeups need an explicit not-advice line
- If evidence is weak, shorter and humbler beats longer and shinier

## Anti-patterns

- **Abstract inflation:** method paragraph longer than results honesty
- **Highlight-reel writing:** only winning seasons
- **Jargon fog** to avoid stating a weak result
- **Disclaimer sandwich:** reckless claim between two polite warnings
- **Roadmap cosplay:** promising future edge that was not shown
- **Single-number myth:** one metric as the whole story

## Output contract

Done means:

- [ ] Claim level labeled in the writeup
- [ ] Setup, validation, baselines present
- [ ] Main result stated without overclaim
- [ ] Non-claims / limits section present
- [ ] Ethics-safe wording
- [ ] Audience-appropriate length
- [ ] Links/refs to experiments or card when available

## Handoffs

- `model-card` if formal contract is missing
- `ethics` for refusal/rewrite on overclaim pressure
- `anti-slop-analytics` for figures/tables
- `backtest-critique` if writeup reveals weak evidence
- `doctrine` if claim level needs re-adjudication
- **Stop** after publishable draft is honest

## Worked example

**Inputs:** paper-level home-win logistic beat rating baseline on walk-forward log-loss, 2018–2024; no odds study.

**Good lead:**
> A simple pre-start home-win model improved walk-forward log-loss versus a rating baseline across 2018–2024. This is a paper result, not a market-edge claim.

**Bad lead:**
> We found a profitable betting edge that beats the books every season.

## References

- `skills/model-card`
- `skills/ethics`
- `skills/doctrine`
- `skills/anti-slop-analytics`
- `skills/experiment-log`
