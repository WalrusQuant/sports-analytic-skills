---
name: feature-rules
description: >
  Design time-safe, leakage-aware features for sports models. Use when
  building feature pipelines, deciding what may enter a model before an
  event, or reviewing whether features could know the future.
version: "0.1.0"
license: MIT
---

# Feature Rules

Modeling-spine skill for sport-agnostic feature design. Features are legal
only if they would have been knowable at the declared prediction timestamp.

## When to use

- Creating or reviewing a feature set
- User says “add more stats” without timing discipline
- Translating box scores / tracking / odds into model inputs
- Preparing inputs for baselines or candidate models
- Before `leakage-audit` on a finished matrix

## When not to use

- Choosing claim level → `doctrine`
- Full audit of an already-built pipeline → `leakage-audit`
- Market line cleaning specifics → `market-data-hygiene`
- Sport-rule encyclopedia dumping with no prediction timestamp

## Required inputs

Minimum:

- Prediction timestamp rule (e.g. scheduled start, lineup lock, midnight before)
- Target variable
- Raw source tables/fields available

Optional:

- Refresh delays (injury reports, official stat corrections)
- Feature store / as-of join support
- Known sport-module constraints (if any)

## Feature legality test

For every candidate feature ask:

> At prediction time T, could an honest analyst have known this value using only information published by T?

If no → illegal.  
If only with delay → shift by delay or drop.  
If partially known → encode the known portion only.

## Feature families (sport-agnostic)

### Usually safe (if time-aligned)

- Prior-event performance aggregates ending before T
- Pre-event market lines available at T (if using markets)
- Schedule context known pre-event (rest days, home/away, travel distance if computed from known schedule)
- Stable roster attributes known pre-event

### Dangerous / often leaked

- Same-event box score fields
- Final score components
- Post-event adjusted stats restated later
- “Season averages” that accidentally include the current event
- Injury/lineup status not yet public at T
- Betting results / closes after T when predicting at open
- Target encodings computed with full-sample leakage

### Conditional

- Opening line vs close: legal only relative to declared T
- In-game features: only for in-game prediction tasks with matching T
- Player availability: only with timestamped source

## Procedure

1. **Declare T (prediction timestamp)**
   - Write it as a rule, not a vibe
   - One T per model claim

2. **Inventory raw fields**
   - Source, grain, update time, correction policy

3. **Propose features with as-of logic**
   - Prefer explicit `as_of_join(entity, T)` patterns
   - Rolling windows must end at last completed event before T

4. **Label each feature**
   - `legal`
   - `illegal`
   - `needs-delay-shift`
   - `needs-source-timestamp`

5. **Block illegal features**
   - Do not “just try them”
   - If user insists, mark experiment as contaminated and claim level `explore` only

6. **Simplify**
   - Strong simple features before giant kitchensink sets
   - Keep a baseline-friendly subset for Tier B models

7. **Emit feature contract**
   - Name, definition, source, grain, legal status, known failure modes

## Hard constraints

- Never include same-event outcome fields in pre-event models
- Never compute aggregates that include the row being predicted
- Never use future market information for earlier decision timestamps
- Never rely on silently corrected historical stats without a versioning rule
- Never treat anonymous “season average” columns as safe without as-of proof
- If timestamps are missing, assume leakage risk is high and say so

## Anti-patterns

- **Join-and-pray:** merge tables on IDs only, ignore times
- **Current-year leakage:** season-to-date includes current game
- **Target sniffing:** encodings built with full dataset target history unordered
- **Injury clairvoyance:** using final inactive list for a model stamped earlier
- **Statboard dump:** 300 features, 0 legality labels
- **Restatement blindness:** official corrected stats treated as available live
- **Window cheat:** rolling(n) computed centered or backward-from-end of season

## Output contract

Done means:

- [ ] Prediction timestamp rule stated
- [ ] Feature list with legality labels
- [ ] As-of / rolling rules specified
- [ ] Illegal features removed or explicitly quarantined
- [ ] Baseline-friendly subset identified
- [ ] Residual timing risks listed
- [ ] Ready for `leakage-audit` or modeling

## Handoffs

- `leakage-audit` — adversarial check of the built matrix/pipeline
- `baseline-models` — use legal simple features in Tier B
- `validation-design` — ensure split logic matches feature availability
- `market-data-hygiene` — if features include odds/lines
- `doctrine` — if feature uncertainty forces claim downgrade
- **Stop** if T cannot be defined; do not model yet

## Worked example

**Request:** “Use team points per game to predict tonight’s winner.”

1. T = scheduled start.
2. Illegal version: season PPG including tonight.
3. Legal version: PPG from completed games before T only, min-games guard.
4. Conditional: if source updates next-day corrections, use snapshot available at T or prior official dump.
5. Output: legal feature `team_ppg_pre_event`, illegal feature rejected `team_ppg_season_final`.

## References

- Leakage audit: `skills/leakage-audit`
- Validation: `skills/validation-design`
- Doctrine time-safety: `skills/doctrine`
