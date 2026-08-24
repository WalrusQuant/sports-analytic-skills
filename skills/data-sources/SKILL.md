---
name: data-sources
description: >
  Choose public sports data sources and loader packages for a modeling question
  across NFL, NBA, MLB, NHL, CFB, soccer, and more. Use before writing
  acquisition code or when an agent is unsure which ecosystem to use — even if
  the user only asks "where do I get data for X." Hands off to nflreadpy,
  sportsdataverse-py, pybaseball, and sports_ds multi-sport CLI paths with a
  written source plan.
version: "0.5.0"
license: MIT
metadata:
  version: "0.5.0"
---

# Data Sources

## Overview

Data-plane skill for **source selection**. Picks an ecosystem and loader path
for the question, then hands off to package skills / `sports_ds` CLI.

Source choice does **not** create predictive value by itself.

---

## When to Use This Skill

Use when:

- “Where do I get data for X?”
- Starting a new sport/league analysis
- Comparing nflverse vs SportsDataverse vs specialist packages
- Before implementing scrapers

Do **not** use when:

- Environment not set up → `environment-setup`
- Source already chosen and loading failed → package skill / debug
- Validation/leakage questions with data already loaded

---

## Required Inputs

- Sport/league
- Grain needed (game, team-game, player-game, pbp, pitch, possession)
- Historical depth needed
- Language preference (Python default here)

---

## Decision Guide (Python-first)

| Need | Prefer first | sports_ds path | Fallback |
|---|---|---|---|
| NFL schedules / team-game panel | nflverse via `nflreadpy` | `sports-ds nfl-eda` / `nfl-win-pipeline` | SDV NFL module |
| NBA team-game | SDV `load_nba_schedule` | `sports-ds nba-eda` / `nba-win-pipeline` | — |
| MLB team-game | SDV MLB Stats API schedule | `sports-ds mlb-eda` / `mlb-win-pipeline` | pybaseball for Statcast depth |
| NHL team-game | SDV `load_nhl_schedule` | `sports-ds nhl-eda` / `nhl-win-pipeline` | skip corrupt season dumps |
| MLB pitch / Statcast | `pybaseball` | skill scripts | SDV person stats |
| CFB / NCAAB / WNBA | SDV league module | (not first-class CLI yet) | — |

Matrix: `references/source_matrix.md`  
Panel contract: `docs/panel-contract.md`  
Ecosystem notes: `docs/data-ecosystem.md`

---

## Workflow

1. Restate the modeling question and grain.
2. List fields required at prediction time T (not every interesting column).
3. Pick the least fragile source that provides those fields.
4. Prefer release/API bulk loaders over live scrapers.
5. Prefer `sports_ds` panel + CLI when the sport is wired (NFL/NBA/MLB/NHL).
6. Document license/ToS posture.
7. Sanity-check home win rate and score variance after load.
8. Snapshot local parquet for reproducible offline analysis.

```bash
python skills/data-sources/scripts/print_source_plan.py
python skills/data-sources/scripts/print_source_plan.py --out data/source_plan.md
```

---

## Hard Constraints

1. Do not default to ToS-hostile scraping when a public loader exists.
2. Do not mix grains casually (pbp rows ≠ game rows) without aggregation rules.
3. Do not ignore delay/as-of issues in “live” APIs.
4. Always note that source choice does not create edge.
5. Snapshot data used for any claim you may need to reproduce.
6. Reject corrupt dumps (constant scores, home-win rate ~0 or ~1).

---

## Anti-Patterns

- Scrape first, ask later
- One giant multi-sport dataframe with incompatible schemas
- Silent source switching mid-experiment
- Using future-enriched vendor stats for pre-event claims
- Handwritten lines/memory as “data”
- Treating a single ESPN scoreboard call as a season schedule

---

## Output Contract

Done means:

- [ ] Sport/grain/time range stated
- [ ] Primary source + package chosen
- [ ] sports_ds CLI/path named when available
- [ ] Fallback source named (or none)
- [ ] License/ToS notes
- [ ] Known coverage gaps / corrupt-season risks listed

---

## Worked Examples

**NFL win model 2018–2024**

- Grain: team-game before kickoff
- Primary: `nflreadpy` via `sports_ds.data.nfl`
- Commands: `sports-ds nfl-eda`, `sports-ds nfl-win-pipeline`

**NBA win model 2023–2024**

- Grain: team-game
- Primary: SDV `load_nba_schedule` via `sports_ds.data.nba`
- Commands: `sports-ds nba-eda`, `sports-ds nba-win-pipeline`
- Install: `pip install -e ".[multi]"`

**MLB win model 2023–2024**

- Grain: team-game
- Primary: SDV MLB Stats API schedule via `sports_ds.data.mlb`
- Commands: `sports-ds mlb-eda`, `sports-ds mlb-win-pipeline`

**NHL win model**

- Prefer known-good end-years (e.g. 2024)
- SDV 2023 dump has been observed corrupt (constant 2–3 scores) — skipped by loader
- Commands: `sports-ds nhl-eda --seasons 2024`, `sports-ds nhl-win-pipeline --seasons 2024`

---

## Bundled Resources

### references/
- `source_matrix.md`
- `tos_notes.md`

### scripts/
- `print_source_plan.py`

---

## Related Skills

- `environment-setup`
- `nflreadpy` / `sportsdataverse-py` / `pybaseball`
- `eda-sports`
- `feature-rules`

---

## Quick Command Card

```bash
python skills/data-sources/scripts/print_source_plan.py --out data/source_plan.md
pip install -e ".[multi]"
sports-ds nba-eda --seasons 2023-2024
sports-ds mlb-eda --seasons 2023-2024
sports-ds nhl-eda --seasons 2024
```
