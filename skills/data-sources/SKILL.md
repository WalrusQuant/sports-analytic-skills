---
name: data-sources
description: >
  Choose public sports data sources for a modeling question across NFL, NBA,
  MLB, NHL, college sports, soccer, and more. Use before acquisition code or
  whenever source coverage, grain, licensing, or historical depth is unclear.
license: MIT
metadata:
  version: "0.12.0"
---

# Data Sources

## Outcome

Produce a written source plan that names the required grain, decision-time
fields, primary source, fallback, coverage risks, license terms, snapshot rule,
and first-load sanity checks. Source choice does not create predictive validity.

## Required inputs

- sport and competition
- analytical question and target
- grain: season, game, team-game, player-game, possession, play, pitch, or event
- historical depth and update cadence
- decision time T for predictive work
- required identifiers and fields
- acceptable license and access constraints

## Decision guide

| Need | Prefer first | Check before committing |
|---|---|---|
| NFL releases and schedules | nflverse through `nflreadpy` | season coverage and schema drift |
| NBA, MLB, NHL, college, soccer | the named public league source or SportsDataverse | endpoint stability and field definitions |
| MLB Statcast or season tables | `pybaseball` | bounded dates and request volume |
| Event data | league-specific public event provider | possession/event identifiers |
| Cross-source enrichment | source with stable IDs and timestamps | join coverage and as-of legality |

Choose the source that natively represents the required grain. Do not begin with
a convenient aggregate and manufacture detail it cannot support.

## Workflow

1. Lock question, grain, target, and decision time.
2. List the minimum fields required to answer the question.
3. Identify two plausible sources and compare coverage, latency, IDs, and terms.
4. Read the source documentation and record field semantics.
5. Pull the smallest representative sample.
6. Validate row counts, uniqueness, time coverage, scores, teams, and null rates.
7. Test joins on a small sample before any full historical pull.
8. Save the raw response or immutable snapshot with retrieval metadata.
9. Record a fallback and the conditions that trigger it.

## First-load checks

- expected seasons and competitions are present
- natural keys are unique at the claimed grain
- completed events have plausible outcomes
- scheduled and completed records are not silently mixed
- identifiers remain stable across seasons
- timestamps have a known timezone and meaning
- duplicate rates and missingness are quantified
- a source/version/retrieval timestamp accompanies every saved artifact

## Hard constraints

- Never scrape when a supported public release or API exists.
- Never merge sources on display names without a documented crosswalk.
- Never treat a current roster or rating as historical without an as-of timestamp.
- Never perform an unbounded pitch-, play-, or event-level pull.
- Never claim coverage until a representative sample has been inspected.
- Respect terms, rate limits, and attribution requirements.

## Artifact schema

Write a Markdown or JSON source plan containing:

```text
question
sport_and_competition
grain
decision_time
required_fields
primary_source
fallback_source
coverage_window
license_and_terms
snapshot_location
retrieved_at
sanity_checks
known_gaps
```

## Helper

```bash
python <path-to-data-sources>/scripts/print_source_plan.py --out data/source_plan.md
```

The output belongs to the user and can be filled before any loader is installed.

## Resources

- `references/source_matrix.md` — ecosystem comparison
- `references/sanity_checks.md` — source-specific checks
- `references/tos_notes.md` — access and attribution reminders
- `scripts/print_source_plan.py` — portable source-plan writer
