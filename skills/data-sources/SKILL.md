---
name: data-sources
description: >
  Choose public sports data sources and loader packages for a modeling
  question across NFL, NBA, MLB, NHL, CFB, soccer, and odds. Use before
  writing acquisition code or when an agent is unsure which ecosystem to use.
version: "0.1.0"
license: MIT
---

# Data Sources

Data-plane skill for source selection. Picks an ecosystem and loader path
for the question, then hands off to package skills.

## When to use

- “Where do I get data for X?”
- Starting a new sport/league analysis
- Comparing nflverse vs SportsDataverse vs specialist packages
- Before implementing scrapers

## When not to use

- Environment not set up → `environment-setup`
- Source already chosen and loading failed → package skill / debug
- Validation/leakage questions with data already loaded

## Required inputs

- Sport/league
- Grain needed (game, team-game, player-game, pbp, pitch, possession)
- Historical depth needed
- Whether odds/market data is required
- Language preference (Python default here)

## Decision guide (Python-first)

| Need | Prefer first | Fallback |
|---|---|---|
| NFL PBP / rosters / weekly stats | `nflreadpy` (nflverse) | `sportsdataverse.nfl` |
| CFB | `sportsdataverse.cfb` / cfbfastR (R) | ESPN endpoints via SDV |
| NBA / WNBA / NCAAB | `sportsdataverse.nba/.wnba/.mbb/.wbb` | league stats endpoints via SDV |
| MLB pitch/statcast depth | `pybaseball` | `sportsdataverse.mlb` |
| NHL | `sportsdataverse.nhl` | R fastRhockey |
| Soccer events | `statsbombpy` (open data) + SDV soccer | FBref tools with ToS care |
| Odds panels | user exports / Odds API / SDV odds | then `market-data-hygiene` |

## Procedure

1. **Restate the modeling question and grain.**
2. **List fields required at prediction time T** (not every interesting column).
3. **Pick the least fragile source that provides those fields.**
4. **Prefer release loaders over live scrapers.**
5. **Document license/ToS posture.**
6. **Hand off to package skill** for concrete load code.
7. **Plan local snapshot** if analysis must be reproducible offline.

## Hard constraints

- Do not default to ToS-hostile scraping when a public loader exists
- Do not mix grains casually (pbp rows ≠ game rows) without aggregation rules
- Do not promise market data if only box scores exist
- Do not ignore delay/as-of issues in “live” APIs
- Always note that source choice does not create edge

## Anti-patterns

- **Scrape first, ask later**
- **One giant multi-sport dataframe** with incompatible schemas
- **Odds from memory** / handwritten lines as “data”
- **Silent source switching** mid-experiment
- **Using future-enriched vendor stats** for pre-event claims

## Output contract

Done means:

- [ ] Sport/grain/time range stated
- [ ] Primary source + package chosen
- [ ] Fallback source named (or none)
- [ ] License/ToS notes
- [ ] Package skill handoff named
- [ ] Known coverage gaps listed

## Handoffs

- `environment-setup` if packages missing
- `nflreadpy` / `sportsdataverse-py` / `pybaseball` for loads
- `market-data-hygiene` for odds panels
- `feature-rules` after data acquisition plan is set

## Worked example

**Question:** pre-game NFL home win model using team form features, 2018–2024.

- Grain: game-level before kickoff
- Primary: `nflreadpy` schedules + team stats / PBP aggregates
- Fallback: none needed for this scope
- Odds: optional later via separate panel
- Handoff: `nflreadpy` → `feature-rules` → `validation-design`

## References

- `docs/data-ecosystem.md`
- nflverse, SportsDataverse, pybaseball project docs
