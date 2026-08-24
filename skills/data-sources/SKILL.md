---
name: data-sources
description: >
  Choose public sports data sources and loader packages for a modeling question
  across NFL, NBA, MLB, NHL, CFB, soccer, and more. Use before writing
  acquisition code or when an agent is unsure which ecosystem to use — even if
  the user only asks "where do I get data for X." Hands off to nflreadpy,
  sportsdataverse-py, pybaseball, and sports_ds multi-sport CLI paths with a
  written source plan, sanity checks, and snapshot rules.
version: "0.6.0"
license: MIT
metadata:
  version: "0.6.0"
---

# Data Sources

## Overview

Data-plane skill for **source selection**.

Pick the least fragile public ecosystem for the grain and question, then hand off
to package skills / `sports_ds` CLI. Source choice does **not** create predictive
value by itself.

This skill is a decision manual, not a scraper kit.

---

## When to Use This Skill

Use when:

- “Where do I get data for X?”
- Starting a new sport/league analysis
- Comparing nflverse vs SportsDataverse vs specialist packages
- Before implementing scrapers
- Choosing between schedule panels vs pbp vs Statcast depth

Do **not** use when:

| Need | Go instead |
|---|---|
| Environment not set up | `environment-setup` |
| Source already chosen and loading failed | package skill / debug |
| Validation/leakage with data already loaded | `validation-design` / `leakage-audit` |
| Feature legality | `feature-rules` |

---

## Installation

```bash
pip install -e .
# multi-sport loaders:
pip install -e ".[multi]"
```

---

## Required Inputs

- Sport/league
- Grain needed (game, team-game, player-game, pbp, pitch, possession)
- Historical depth needed
- Fields required at decision time T (if predictive)
- Language preference (Python default here)

---

## Decision Guide (Python-first)

| Need | Prefer first | sports_ds path | Fallback |
|---|---|---|---|
| NFL schedules / team-game panel | nflverse via `nflreadpy` | `nfl-eda`, `nfl-win-pipeline`, `nfl-margin-pipeline`, `nfl-elo` | SDV NFL module |
| NBA team-game | SDV `load_nba_schedule` | `nba-eda`, `nba-win-pipeline`, `nba-margin-pipeline`, `nba-elo` | — |
| MLB team-game | SDV MLB Stats API schedule | `mlb-eda`, `mlb-win-pipeline`, `mlb-margin-pipeline`, `mlb-elo` | — |
| MLB pitch / Statcast | `pybaseball` | skill scripts | SDV person stats |
| NHL team-game | SDV `load_nhl_schedule` | `nhl-eda` (historical dumps often corrupt) | alternate source later |
| CFB / NCAAB / WNBA | SDV league module | not first-class CLI yet | — |
| Soccer events | SDV soccer / open event data | not first-class CLI yet | ToS-careful sources |

Matrix: `references/source_matrix.md`  
ToS notes: `references/tos_notes.md`  
Panel contract: `docs/panel-contract.md`  
Ecosystem notes: `docs/data-ecosystem.md`

---

## Workflow

1. Restate the modeling question and grain in one sentence.
2. List fields required at prediction time T (not every interesting column).
3. Pick the least fragile source that provides those fields.
4. Prefer release/API bulk loaders over live scrapers.
5. Prefer `sports_ds` panel + CLI when the sport is wired (NFL/NBA/MLB).
6. Document license/ToS posture.
7. Load a small window and **sanity-check**:
   - row counts
   - seasons present
   - home win rate not ~0 or ~1
   - score variance not constant
8. Snapshot local parquet for reproducible offline analysis.
9. Hand off to `eda-sports` → `feature-rules` → modeling skills.

```bash
python skills/data-sources/scripts/print_source_plan.py
python skills/data-sources/scripts/print_source_plan.py --out data/source_plan.md
```

---

## Sanity Checks After First Load

| Check | Healthy signal | Bad signal |
|---|---|---|
| Overall win rate on team-game panel | ~0.5 | 0.0 / 1.0 |
| Home win rate (`is_home==1`) | ~0.52–0.60 depending on sport | <0.40 or >0.70 unexplained |
| Unique score pairs | many | 1–2 constant pairs |
| Duplicate game_id | 0 after dedupe | many |
| Season labels | match request | missing/shifted years |

Reject corrupt dumps. Do not model them.

---

## Hard Constraints

1. Do not default to ToS-hostile scraping when a public loader exists.
2. Do not mix grains casually (pbp rows ≠ game rows) without aggregation rules.
3. Do not ignore delay/as-of issues in “live” APIs.
4. Always note that source choice does not create edge.
5. Snapshot data used for any claim you may need to reproduce.
6. Reject corrupt dumps (constant scores, home-win rate ~0 or ~1).
7. Prefer bulk season loaders over single-day scoreboard calls for historical panels.

---

## Anti-Patterns

- Scrape first, ask later
- One giant multi-sport dataframe with incompatible schemas
- Silent source switching mid-experiment
- Using future-enriched vendor stats for pre-event claims
- Handwritten lines/memory as “data”
- Treating a single ESPN scoreboard call as a season schedule
- Modeling before sanity checks

---

## Output Contract

Done means:

- [ ] Sport/grain/time range stated
- [ ] Primary source + package chosen
- [ ] sports_ds CLI/path named when available
- [ ] Fallback source named (or none)
- [ ] License/ToS notes
- [ ] Known coverage gaps / corrupt-season risks listed
- [ ] First-load sanity checks planned or done

---

## Worked Examples

### NFL win model 2018–2024
- Grain: team-game before kickoff
- Primary: `nflreadpy` via `sports_ds.data.nfl`
- Commands:
  - `sports-ds nfl-eda --seasons 2018-2024`
  - `sports-ds nfl-win-pipeline --seasons 2018-2024`

### NBA win/margin/Elo 2023–2024
- Install: `pip install -e ".[multi]"`
- Commands:
  - `sports-ds nba-eda --seasons 2023-2024`
  - `sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1`
  - `sports-ds nba-margin-pipeline --seasons 2023-2024 --min-train-seasons 1`
  - `sports-ds nba-elo --seasons 2023-2024 --min-train-seasons 1`

### MLB team-game vs Statcast
- Team-game outcomes → `sports-ds mlb-*`
- Pitch-level Statcast → `pybaseball` skill, bounded dates

### Source plan artifact
```bash
python skills/data-sources/scripts/print_source_plan.py --out data/source_plan.md
```

---

## Bundled Resources

### references/
- `source_matrix.md`
- `tos_notes.md`
- `sanity_checks.md`

### scripts/
- `print_source_plan.py`

---

## Related Skills

- `environment-setup`
- `nflreadpy` / `sportsdataverse-py` / `pybaseball`
- `eda-sports`
- `feature-rules`
- `sports-modeling-doctrine`

---

## Quick Command Card

```bash
python skills/data-sources/scripts/print_source_plan.py --out data/source_plan.md
pip install -e ".[multi]"
sports-ds nfl-eda --seasons 2023-2024
sports-ds nba-eda --seasons 2023-2024
sports-ds mlb-eda --seasons 2023-2024
```
