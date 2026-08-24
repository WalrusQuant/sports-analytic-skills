---
name: ethics
description: >
  Enforce honesty bounds for sports analytics: no fake certainty, no locks,
  no guaranteed-+EV language, and clear not-advice posture. Use when writing
  claims, public posts, model summaries, or refusing tip-shop requests.
version: "0.1.0"
license: MIT
---

# Ethics

Honesty and refusal skill for Sports Analytic Skills. This skill governs
**what may be claimed** and **what must be refused**. It does not decide
whether a model passed validation — that is `doctrine`.

## When to use

- Drafting any public or user-facing claim about a model
- User asks for picks, locks, “sure things,” or guaranteed profit language
- Agent is about to overstate confidence
- Packaging results for README, post, notebook, or report
- Reviewing whether a statement is advice-shaped

## When not to use

- Choosing metrics, splits, or baselines → `doctrine` / `validation-design`
- Stake sizing math and ruin framing details → `risk`
- Deep leakage inspection mechanics → `leakage-audit`
- Ordinary code help with no external claim

## Required inputs

- The draft claim or user request
- Claim level already earned under `doctrine` (`explore` / `paper` / `market-relative` / `kill`)
- Audience (private notes, public post, end user, agent output)

If claim level is unknown, run a short `doctrine` pass first.

## Honesty principles

1. **Say what the evidence supports — nothing more**
2. **Uncertainty is required, not optional flavor text**
3. **Not-advice is real:** methodology is not a personal betting instruction
4. **Refuse tip-shop framing** even if a model is decent
5. **Reproducibility over mystique**
6. **No fabricated precision** (fake p-values, fake CLV, fake records)

## Procedure

1. **Classify the request**
   - Methodology / modeling help
   - Evaluation / critique
   - Public communication
   - Pick service / lock request / guaranteed money request

2. **If tip-shop or guarantee request → refuse**
   - Explain this library does methodology, not picks
   - Offer allowed alternative: validation, critique, baseline design, claim card

3. **Bind claims to earned claim level**

| Earned level | Allowed language | Banned language |
|---|---|---|
| `explore` | “hypothesis”, “worth testing”, “preliminary” | works, edge, beat the market |
| `paper` | “out-of-sample vs baselines”, “paper model”, limits | lock, sure bet, guaranteed +EV |
| `market-relative` | cautious market-relative statements with evidence and limits | certainty, inevitable profit |
| `kill` | “failed gate”, “do not use as edge” | salvaging hype |

4. **Strip or rewrite overclaim verbs**
   - Replace: lock, cinch, print, guaranteed, can’t lose, easy money
   - Prefer: estimate, out-of-sample, calibrated, failed, unresolved

5. **Add required disclosures for external claims**
   - Not financial/betting advice
   - Sample period and validation method
   - What was **not** tested
   - Failure conditions

6. **Check for misleading presentation**
   - Cropped axes / selected dates / hidden vig / omitted losing segments
   - Leaderboard metrics that ignore time leakage
   - “Profit” plots without costs, limits, or uncertainty

7. **Final ethics verdict**
   - `approve` — claim matches evidence and tone
   - `rewrite` — fixable overclaim
   - `refuse` — tip-shop, guarantee, or dishonest framing

## Hard constraints

- Never provide “locks of the day” or pick lists as a product of these skills
- Never claim guaranteed profit or risk-free edge
- Never present exploration work as proven edge
- Never invent results, CLV, records, or citations
- Never hide failed validations to protect a narrative
- Never imply this software places bets or manages bankroll
- Always include not-advice posture on public/actionable-facing outputs
- If pressed to overclaim, refuse rather than soften into junk

## Anti-patterns

- **Authority laundering:** “the AI model says bet X”
- **Certainty cosplay:** 53% model shown as a lock
- **Advice disguise:** “for educational purposes” attached to a pick slate
- **Record fiction:** unverifiable ROI screenshots as proof
- **Vig amnesia:** quoting odds edges without transaction reality
- **Selected highlight reels:** showing only winning weeks
- **Fake humility:** long disclaimer followed by the same reckless claim
- **Harassment of uncertainty:** deleting error bars because they “look weak”

## Output contract

Done means:

- [ ] Request classified
- [ ] Ethics verdict: `approve` / `rewrite` / `refuse`
- [ ] If rewrite: corrected claim text with claim level labeled
- [ ] If refuse: clear reason + allowed alternative path
- [ ] Disclosures included when audience is public or decision-facing
- [ ] No locks / guarantees / fabricated metrics remain

## Refusal templates (adapt as needed)

**Picks / locks**

> I won’t provide locks or pick slates. I can help design a validation plan, critique a model, or write an honest claim card from evidence you provide.

**Guaranteed profit**

> No valid sports model offers guaranteed profit. If you want, we can test whether a process beats baselines out of sample and what it still does not prove.

**Overclaim rewrite cue**

> This result supports a `paper` claim only: time-safe improvement vs baselines over period S. It does not justify market-action language without market-relative evaluation.

## Handoffs

- `doctrine` — claim level not established
- `risk` — need uncertainty/stake-discipline wording after claim is honest
- `backtest-critique` — evaluate an existing system’s evidence quality
- `model-card` / `edge-writeup` — durable honest documentation
- `anti-slop-analytics` — presentation cleanup (when that skill exists)
- **Stop** after `refuse` unless user accepts a methodology path

## Worked example

**Request:** “Give me tonight’s locks from the model. Mark them guaranteed +EV.”

1. Classify: tip-shop + guarantee.
2. Verdict: `refuse`.
3. Alternative offered:
   - define target and baselines
   - run/critique walk-forward
   - if evidence exists, write a `paper` or `market-relative` claim card with limits
4. No picks produced.

**Request:** “Summarize this walk-forward where we beat baseline log-loss for 3 seasons, no odds data.”

1. Claim level earned: `paper` (assuming doctrine/validation agree).
2. Approve only language like: “paper model improved vs baseline under time-safe validation; not market-proven.”
3. Ban: “beat the books”, “locks”, “print money”.

## References

- Repo disclaimer: `LICENSE`, root `README.md`
- Doctrine claim levels: `skills/doctrine`
- Communication later skills: `edge-writeup`, `anti-slop-analytics` (planned)
