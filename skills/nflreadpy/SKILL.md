---
name: nflreadpy
description: >
  Load NFL data with nflreadpy (nflverse Python loader): play-by-play,
  schedules, rosters, player/team stats, and related releases. Use for NFL
  acquisition before feature building or validation.
version: "0.1.0"
license: MIT
---

# nflreadpy

Package skill for the nflverse Python loader. This is the default NFL data
path for this repo.

Upstream: [nflverse/nflreadpy](https://github.com/nflverse/nflreadpy)

## When to use

- Any NFL historical modeling/analysis task
- Need PBP, weekly player stats, rosters, schedules, injuries, snap counts
- Replacing ad-hoc nflfastR CSV URL scraping in Python

## When not to use

- Non-NFL leagues → `sportsdataverse-py` / other specialists
- Environment missing → `environment-setup`
- Odds panel cleaning → `market-data-hygiene`

## Required inputs

- Seasons or season range
- Tables needed (pbp, schedules, rosters, stats, …)
- Whether pandas or polars is desired downstream

## Install

```bash
pip install nflreadpy
# or with repo data bundle:
pip install -r requirements/python-data.txt
```

Recommended cache:

```bash
export NFLREADPY_CACHE=filesystem
export NFLREADPY_CACHE_DIR="$HOME/.cache/nflreadpy"
```

## Procedure

1. Import and configure cache if needed.
2. Load only required seasons/tables.
3. Inspect schema and season coverage.
4. Convert to pandas only if necessary (`df.to_pandas()`).
5. Persist a local parquet snapshot for reproducibility when running experiments.
6. Hand off to `feature-rules` with an explicit prediction timestamp T.

## Common loads

```python
import nflreadpy as nfl

pbp = nfl.load_pbp([2022, 2023, 2024])
schedules = nfl.load_schedules([2022, 2023, 2024])
player_stats = nfl.load_player_stats([2022, 2023, 2024])
team_stats = nfl.load_team_stats([2022, 2023, 2024])
rosters = nfl.load_rosters([2024])
injuries = nfl.load_injuries([2024])
```

Useful extras: `load_snap_counts`, `load_nextgen_stats`, `load_depth_charts`,
`load_draft_picks`, `load_participation`, `load_contracts`.

## Scripts in this skill

- `scripts/smoke_load.py` — import + tiny load sanity check
- `scripts/load_game_panel.py` — example schedule panel to parquet

Run:

```bash
python skills/nflreadpy/scripts/smoke_load.py
python skills/nflreadpy/scripts/load_game_panel.py --seasons 2023,2024 --out data/nfl_schedules.parquet
```

## Hard constraints

- Prefer official nflverse releases via nflreadpy over random mirrors
- Do not treat PBP columns as pre-snap features without timing review
- Snapshot data used in a paper claim (`experiment-log`)
- Respect dataset licenses (mostly CC-BY; verify exceptions)
- Keep raw downloads out of git unless explicitly curated sample data

## Anti-patterns

- Downloading all seasons every session with cache off
- Joining final rosters onto pre-game rows without as-of logic
- Using post-play PBP fields to “predict” the same play
- Silent pandas/polars conversion bugs on dtypes

## Output contract

Done means:

- [ ] Required tables loaded for requested seasons
- [ ] Row counts / season coverage reported
- [ ] Cache mode noted
- [ ] Optional parquet snapshot path noted
- [ ] Handoff to feature/validation skills ready

## Handoffs

- `feature-rules` / `leakage-audit`
- `baseline-models` / `validation-design`
- `experiment-log` for snapshot + version notes
- `data-sources` if NFL is the wrong league

## Worked example

Build a game-level schedule panel for 2023–2024, save parquet, then design
pre-game features only from information available before `gameday` kickoff
time using `feature-rules`.

## References

- https://github.com/nflverse/nflreadpy
- https://github.com/nflverse/nflverse-data
- `docs/data-ecosystem.md`
