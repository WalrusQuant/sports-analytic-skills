---
name: data-sources
description: >
  Choose public sports data sources and loader packages for a modeling question
  across NFL, NBA, MLB, NHL, CFB, soccer, and more. Use before writing
  acquisition code or when an agent is unsure which ecosystem to use — even if
  the user only asks "where do I get data for X." Hands off to nflreadpy,
  sportsdataverse-py, or pybaseball with a written source plan.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# Data Sources

## Overview

Data-plane skill for **source selection**. Picks an ecosystem and loader path
for the question, then hands off to package skills.

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

| Need | Prefer first | Fallback |
|---|---|---|
| NFL PBP / rosters / weekly / schedules | `nflreadpy` (nflverse) | `sportsdataverse` NFL module |
| CFB | `sportsdataverse` CFB | — |
| NBA / WNBA / NCAAB | `sportsdataverse` | — |
| MLB pitch / Statcast depth | `pybaseball` | `sportsdataverse` MLB |
| NHL | `sportsdataverse` NHL | — |
| Soccer events | SDV soccer; optional StatsBomb later | ToS-careful open event data |

Matrix: `references/source_matrix.md`  
Ecosystem notes: `docs/data-ecosystem.md`

---

## Workflow

1. Restate the modeling question and grain.
2. List fields required at prediction time T (not every interesting column).
3. Pick the least fragile source that provides those fields.
4. Prefer release loaders over live scrapers.
5. Document license/ToS posture.
6. Hand off to package skill for concrete load code.
7. Plan local snapshot if analysis must be reproducible offline.

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

---

## Anti-Patterns

- Scrape first, ask later
- One giant multi-sport dataframe with incompatible schemas
- Silent source switching mid-experiment
- Using future-enriched vendor stats for pre-event claims
- Handwritten lines/memory as “data”

---

## Output Contract

Done means:

- [ ] Sport/grain/time range stated
- [ ] Primary source + package chosen
- [ ] Fallback source named (or none)
- [ ] License/ToS notes
- [ ] Package skill handoff named
- [ ] Known coverage gaps listed

---

## Worked Example

**Question:** pre-game NFL team win model using team form features, 2018–2024.

- Grain: team-game before kickoff
- Primary: `nflreadpy` schedules via `sports_ds.data.nfl`
- Fallback: none needed for this scope
- Handoff: `nflreadpy` → `eda-sports` → `feature-rules` → `validation-design`

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
```
