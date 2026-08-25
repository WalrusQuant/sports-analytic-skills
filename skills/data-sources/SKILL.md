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

## When to Use This Skill

Use when:

- the user needs a public sports data source and is not sure which one;
- choosing grain (game, team-game, player-game, play/event) before loading;
- comparing nflverse / sportsdataverse / pybaseball / other public options;
- writing a source plan with provenance, snapshot, and first-load checks.

Do **not** use this skill when:

- the user already has a usable table and wants EDA or modeling;
- they explicitly want the optional repository toolkit panels/CLI → `sports-ds-bridge`;
- they already chose a loader and just need that loader skill.

| Need | Go instead |
|---|---|
| NFL loader details | `nflreadpy` |
| Multi-sport SDV details | `sportsdataverse-py` |
| MLB / Statcast details | `pybaseball` |
| Optional toolkit bridge | `sports-ds-bridge` |
| EDA after load | `eda-sports` |

## Outcome

Produce a source plan naming the required grain, decision-time fields, primary
source, fallback, coverage risks, terms, snapshot rule, and first-load checks.
Source choice does not create predictive validity; it determines whether the
question can be answered reproducibly and legally.

Use this skill before acquisition code or whenever coverage, field semantics,
historical depth, IDs, latency, or licensing are uncertain. If the source is
already chosen and a loader fails, use its package skill instead.

## Required inputs

- sport, competition, question, target, and analytical population;
- analytical grain and natural key: season, game, team-game, player-game,
  possession, play, pitch, or event;
- each candidate source's native grain and the aggregation/join contract needed
  to reach the analytical grain;
- historical depth, expected volume, refresh cadence, and completion latency;
- exact prediction decision time T and fields that must be known by then;
- stable identifiers and cross-source joins required;
- license, attribution, redistribution, authentication, and rate constraints;
- required raw and derived artifact formats.

## Candidate guide

These are ecosystems to investigate, not durable rankings. Confirm current
coverage, access, and terms in upstream documentation at selection time.

| Need | Candidate ecosystem | Verify before committing |
|---|---|---|
| NFL schedules, PBP, rosters, weekly data | nflverse / `nflreadpy` | table-specific grain, season coverage, schema drift |
| Basketball, hockey, college, soccer | maintained league/public modules, including SportsDataverse where applicable | competition/table support and field definitions |
| MLB Statcast/pitch or season tables | public MLB data tooling such as `pybaseball` | query-specific grain, bounded dates, field availability |
| Detailed event/possession data | public league-specific event provider | event IDs, ordering, correction policy |
| Cross-source enrichment | sources with stable IDs and timestamps | join coverage and as-of legality |

Read [the source matrix](references/source_matrix.md) while shortlisting
ecosystems, [the terms notes](references/tos_notes.md) before acquisition or
redistribution, and [the sanity checks](references/sanity_checks.md) before
accepting the first pull.

Choose a source whose native records contain the facts required for the
analytical grain, and write the aggregation contract when the grains differ.
For example, play data may be aggregated to team-game only after event ordering,
completion, and key rules are explicit. A season aggregate cannot manufacture
play-level detail or historical publication vintages it never contained.

## Source comparison rubric

Compare at least two plausible sources on:

| Dimension | Questions |
|---|---|
| Coverage | Which competitions, seasons, phases, and entities exist? |
| Grain | What is one native record and its key? If it differs from the analytical grain, is the transformation explicit and valid? |
| Semantics | Are fields, units, ties, overtime, and completion states defined? |
| Time | Event, publication, update, and revision timestamps available? |
| Identity | Stable event/team/player IDs across seasons and sources? |
| Reliability | Bulk releases, versioning, uptime, schema-change notices? |
| Access | Terms, license, attribution, auth, rate and redistribution limits? |
| Reproducibility | Can responses be snapshotted and checksummed? |
| Cost/volume | Can the bounded request fit time, memory, storage, and quotas? |

Do not treat “popular” or “easy to import” as sufficient evidence.

## Workflow

1. Lock question, analytical grain/key, target, population, and T.
2. List only the minimum required raw fields and stable identifiers.
3. Shortlist and compare a primary and fallback source with the rubric.
4. Read upstream documentation and record field/time semantics and terms.
5. Estimate request count and data volume; bound event-level pulls by dates/IDs.
6. Pull the smallest representative sample spanning relevant eras/statuses.
7. Validate keys, row counts, periods, outcomes, entities, timestamps, and nulls.
8. Test required joins on a small sample and quantify unmatched/many-to-many rows.
9. Save the untouched raw response or immutable snapshot with retrieval metadata.
10. Document fallback triggers, known gaps, and the EDA handoff.

## First-load diagnostics

- nonzero rows and requested competitions/seasons are present;
- natural keys are unique at the claimed grain;
- scheduled, live, completed, canceled, and postponed records are distinguishable;
- completed events have plausible outcomes and nonconstant score distributions;
- team-game overall win rate is near its paired identity and home-only rates are plausible;
- identifiers remain stable or have a documented crosswalk;
- timestamps have known timezone and meaning;
- critical missingness is measured by season/status/source;
- source/version/query/retrieval time accompany every saved artifact.

```python
key = ["game_id", "team"]
assert len(df) > 0
print(df["season"].value_counts().sort_index())
print("duplicate key rows:", df.duplicated(key).sum())
print(df.groupby("status")["game_id"].nunique())
print(df.isna().mean().sort_values(ascending=False).head(20))
```

Reject corrupt or mis-grained pulls rather than adapting the question silently.

## Snapshot and provenance policy

Preserve raw responses before normalization. Record source/project version,
endpoint or release, exact parameters, requested/retrieved times in UTC, schema
fingerprint, row count, checksum, timezone, license/attribution, and any later
correction policy. Derived tables should point to immutable raw snapshots and
transformation code/config. Never overwrite data referenced by an experiment.

For predictive work, a current bulk snapshot may contain revisions unavailable
historically. State whether the study reconstructs real-time vintages or accepts
revised-history data and limit claims accordingly.

## Hard constraints and anti-patterns

| Do not | Why |
|---|---|
| scrape when a supported release/API exists | fragile and may violate terms |
| merge display names without a crosswalk | silent false matches and duplicates |
| use current roster/rating as historical | post-T information leaks backward |
| run unbounded pitch/play/event pulls | rate, memory, and reproducibility risk |
| switch sources mid-experiment silently | changes population and semantics |
| mix grains without an aggregation contract | estimand and independence change |
| infer season coverage from one scoreboard call | endpoint purpose is different |
| model before representative checks | corrupt data becomes plausible output |

Respect terms, rate limits, access controls, and attribution. Never evade a
provider restriction. Cache only when permitted.

## Worked source plans

**NFL pre-kickoff win model:** team-game grain; nflverse schedules/results via
`nflreadpy`; require stable game/team IDs, scheduled start, home/away, completion
state, and scores for labels. Check schema across requested seasons and snapshot
the release. Use a documented public fallback only if coverage fails.

**MLB pitch analysis:** pitch grain; `pybaseball` Statcast; bound every request by
date and test a small window. Verify `game_pk`, at-bat/pitch order, units, missing
tracking fields, doubleheaders, and revision behavior before scaling the pull.

**Cross-source injury enrichment:** select sources with stable player/team IDs
and publication timestamps. Build a reviewed crosswalk, measure unmatched joins,
and require an as-of predicate. If historical timestamps are absent, the source
cannot support the intended pre-event claim.

## Source-plan artifact

```text
Question / sport / competition / target:
Analytical grain and natural key / population / decision time T:
Required fields and IDs:
Primary source and rationale:
Primary native grain/key and aggregation contract:
Fallback and trigger:
Fallback native grain/key and compatibility with primary:
Coverage window / status handling:
Event, publication, revision semantics:
License, terms, attribution, access limits:
Estimated request/volume and bounded query:
Representative sample checks:
Join checks and crosswalk:
Raw snapshot location / checksum / retrieved_at:
Known gaps and claim limitations:
EDA handoff:
```

Create the portable stub with:

```bash
python /path/to/data-sources/scripts/print_source_plan.py --out data/source_plan.md
```

## Integrity and resource routing

1. Never claim coverage until a representative sample is inspected.
2. Preserve raw snapshots and provenance for every reproducible claim.
3. Source timestamps and revision policy are part of feature legality.
4. Read `source_matrix.md` for ecosystem choice, `tos_notes.md` for access and
   redistribution, and `sanity_checks.md` before accepting data.
5. Hand off loaded data to `eda-sports`, then `feature-rules` and validation.
