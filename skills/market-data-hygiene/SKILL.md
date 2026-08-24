---
name: market-data-hygiene
description: >
  Clean and standardize sports odds/market panels: timestamps, open/close,
  vig, missingness, and join keys. Use before CLV work or any model feature
  that consumes lines.
version: "0.1.0"
license: MIT
---

# Market Data Hygiene

Market-layer skill for making odds data trustworthy enough to use. Bad
market panels create fake edges. This skill standardizes lines before
modeling or CLV evaluation.

## When to use

- Ingesting odds from books, exchanges, or vendors
- Building features from open/close lines
- Preparing panels for `clv-evaluation`
- Investigating missing/broken line history

## When not to use

- Offline modeling with no market data
- Claim ethics / pick refusals → `ethics`
- Full market-relative performance judgment → `clv-evaluation`
- Generic non-odds feature timing → `feature-rules`

## Required inputs

Minimum:

- Raw odds records
- Event identifiers and scheduled start times
- Field dictionary (what each column means)

Optional:

- Book identifiers
- Line types (moneyline, spread, total, prop)
- Known vendor delay/snapshot behavior

## Hygiene checklist

1. **Identity**
   - Stable event IDs
   - Side/team normalization
   - Market type normalization

2. **Timestamps**
   - Line timestamp timezone explicit (store UTC)
   - Distinguish snapshot time vs event start
   - Define open and close rules

3. **Quote validity**
   - Remove zero/negative prices
   - Handle suspended/missing markets
   - Detect stale quotes pasted across events

4. **Vig / pricing form**
   - Convert to a common form (e.g. American → implied prob)
   - Record whether prices are two-way and vig-inclusive
   - Do not mix probability units silently

5. **Open/close definitions**
   - Open = first reliable quote in window, or official open if provided
   - Close = last reliable quote at/before start (or declared cutoff)
   - Document book-specific quirks

6. **Missingness**
   - Rate of missing opens/closes by book/season
   - Do not impute closes with post-start data

7. **Joins to model tables**
   - as-of join at prediction timestamp T
   - Never join “final close” into an earlier T without label

## Procedure

1. Profile raw panel (counts, books, market types, date range).
2. Normalize teams/sides/markets.
3. Enforce timestamp validity and sort order.
4. Define open/close algorithm and apply it.
5. Convert prices to analysis units; retain raw.
6. Compute data-quality report:
   - coverage
   - missing close rate
   - median vig
   - outlier moves
7. Emit clean panel + quality report + join keys.
8. Only then allow market features or CLV metrics.

## Hard constraints

- Never use post-start quotes as pre-start closes
- Never silently average books with incompatible market definitions
- Never drop losing sides through quiet filters
- Never treat missing close as zero move
- Always keep provenance: source, book, snapshot rule
- If close definition is ambiguous, mark panel `suspect` for market claims

## Anti-patterns

- **Close-from-future:** first quote after tip used as close
- **Book soup:** mixing exchange mid with retail quotes unlabeled
- **Vig amnesia**
- **Orphan lines:** quotes with no event start
- **Survivor bias:** only events with complete line histories kept without disclosure

## Output contract

Done means:

- [ ] Normalized market panel
- [ ] Open/close rules documented
- [ ] Price units documented
- [ ] Quality report produced
- [ ] Known defects listed
- [ ] Safe join guidance at timestamp T
- [ ] Panel status: `clean` / `suspect` / `unusable`

## Handoffs

- `clv-evaluation` — once panel status is `clean` or explicitly accepted `suspect`
- `feature-rules` — if lines become model features
- `leakage-audit` — if market joins are complex
- `doctrine` — if data quality caps claim level
- **Stop** if panel is `unusable`

## Worked example

**Raw issue:** closes timestamped minutes after start for some games.  
**Fix:** redefine close as last quote with `line_ts <= scheduled_start`.  
**Report:** 4.2% games lose close under new rule; those rows excluded from CLV, not filled forward.  
**Status:** `clean` for remaining rows.

## References

- `skills/clv-evaluation`
- `skills/feature-rules`
- `skills/leakage-audit`
