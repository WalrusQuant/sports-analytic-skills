---
name: pybaseball
description: >
  Load MLB data with pybaseball (Statcast/Savant, batting/pitching tables, and
  related public baseball sources). Use for baseball acquisition and pitch-level
  or season-aggregate pulls in Python — even if the user only says "get Statcast"
  or "pull MLB batting stats." Includes bounded-pull guidance, smoke scripts,
  and feature-legality handoff.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# pybaseball

## Overview

Package skill for https://github.com/jldbc/pybaseball

Use for MLB pitch-level Statcast and season batting/pitching tables when you need baseball depth beyond generic multi-sport loaders.

---

## When to Use This Skill

Use when:

- MLB pitch-level Statcast analyses
- Season batting/pitching tables from public baseball sources
- Python baseball workflows where SportsDataverse MLB is not enough

Do **not** use when:

- Non-baseball leagues
- Environment missing → `environment-setup`
- Simple MLB API person stats already covered by SDV and already working

---

## Installation

```bash
pip install -e ".[multi]"
# or
pip install pybaseball
```

---

## Required Inputs

- Date range and/or season
- Entity (player, team, league-wide)
- Grain (pitch, game, season)

---

## Workflow

1. Define grain and date window.
2. Pull the **smallest** table that answers the question.
3. Cache/snapshot results to parquet.
4. Document source function used (Statcast vs season tables).
5. Pass through `feature-rules` before pre-pitch/pre-game claims.

---

## Example Loads

```python
from pybaseball import statcast, batting_stats, pitching_stats

# pitch-level (can be large) — bound dates
# pitches = statcast("2024-04-01", "2024-04-07")

batting = batting_stats(2024)
pitching = pitching_stats(2024)
```

Patterns: `references/pull_patterns.md`

---

## Scripts

```bash
python skills/pybaseball/scripts/smoke_load.py
```

---

## Hard Constraints

1. Statcast pulls can be huge — bound dates.
2. Scrapers break; log package version and date.
3. Do not hammer endpoints in tight loops.
4. Pitch-level fields are not automatically legal pre-pitch features.
5. Snapshot any dataset used for a claim you may need to reproduce.

---

## Anti-Patterns

- Pulling full-season Statcast for a tiny question
- No local cache/snapshot
- Silent retries that look like hanging agents
- Mixing FanGraphs/Reference definitions without mapping

---

## Output Contract

Done means:

- [ ] Grain/window stated
- [ ] Load succeeded or failed clearly
- [ ] Row counts reported
- [ ] Snapshot path optional but recommended
- [ ] Handoff to feature/validation skills

---

## Bundled Resources

### references/
- `pull_patterns.md`
- `statcast_bounds.md`

### scripts/
- `smoke_load.py`

---

## Related Skills

- `sportsdataverse-py` for alternate MLB API paths
- `environment-setup`
- `data-sources`
- `feature-rules` / `leakage-audit`
- `experiment-log`

---

## Quick Command Card

```bash
pip install -e ".[multi]"
python skills/pybaseball/scripts/smoke_load.py
```
