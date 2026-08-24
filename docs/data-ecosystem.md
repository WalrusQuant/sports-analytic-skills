# Data ecosystem

Public sports data sources and loader packages for modeling and analysis.

## Primary ecosystems

### nflverse (NFL)

| Piece | Role |
|---|---|
| nflverse-data | hosted releases |
| nflreadpy | Python loader (default here) |
| nflreadr / nflfastR | R ecosystem |

Loads: PBP, schedules, rosters, player/team stats, injuries, snaps, etc.

### SportsDataverse (multi-sport)

Python package: `sportsdataverse`

Common modules: NBA, WNBA, NCAAB, CFB, NFL, MLB, NHL, soccer, and more.

R sisters: hoopR, wehoop, cfbfastR, baseballr, fastRhockey, etc.

### Baseball specialists

- `pybaseball` — Statcast/Savant and season tables
- SportsDataverse MLB module as alternate path

### Soccer

- SportsDataverse soccer module
- optional later: statsbombpy and other open event-data tools

## Recommended Python stack

```text
numpy pandas polars pyarrow
scipy scikit-learn statsmodels matplotlib
nflreadpy sportsdataverse pybaseball
```

See `requirements/python-data.txt` and `docs/environment.md`.

## After loading data

1. EDA (`eda-sports`)
2. time-safe features (`feature-rules`)
3. baselines + models
4. validation
5. interpretation / reporting

Loading data is not analysis.

## Optional toolkit adapter

When the user explicitly wants repository-provided normalized panels or CLI
loaders, use `sports-ds-bridge`. Export CSV or Parquet and continue with the
standalone skill; do not make downstream skills import the toolkit.
