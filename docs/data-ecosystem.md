# Data ecosystem

This library’s first 15 skills are the **judgment layer** (how to model honestly).  
K-Dense-style usefulness also needs a **data plane**: which packages to install, what they load, and how agents should call them.

This document maps the public sports-data ecosystems agents should know.

## Two layers in this repo

| Layer | Job | Examples in this repo |
|---|---|---|
| Judgment | doctrine, leakage, validation, claims | `doctrine`, `validation-design`, … |
| Data / packages | install, load, cache, source-specific gotchas | `environment-setup`, `nflreadpy`, `sportsdataverse-py`, … |

Judgment skills stay source-agnostic. Package skills teach concrete loaders.  
Always bind loaded data back through `feature-rules` + `leakage-audit` before claims.

## Primary ecosystems

### 1) nflverse (NFL)

Best-in-class open NFL stack.

| Piece | Role | Language |
|---|---|---|
| [nflverse-data](https://github.com/nflverse/nflverse-data) | hosted releases (csv/parquet/rds/qs) | data |
| [nflreadr](https://nflreadr.nflverse.com) | R loader | R |
| [nflreadpy](https://github.com/nflverse/nflreadpy) | Python loader (Polars) | Python |
| [nflfastR](https://www.nflfastr.com) | PBP scrape + EPA/WPA style modeling (R) | R |
| nflplotR / nfl4th / nflseedR | plot, 4th down, season sim | R |

**Python default for this repo:** `nflreadpy`

Common loads:

- `load_pbp()`
- `load_player_stats()` / `load_team_stats()`
- `load_schedules()`, `load_rosters()`, `load_rosters_weekly()`
- `load_snap_counts()`, `load_nextgen_stats()`, `load_injuries()`
- `load_depth_charts()`, `load_draft_picks()`, `load_contracts()`

License note: most nflverse data is broadly CC-BY 4.0; some charting sets differ (check current nflverse docs).

### 2) SportsDataverse (multi-sport)

Open multi-league family (R / Python / JS).

**Python flagship:** `sportsdataverse` (`pip install sportsdataverse`)

Modules commonly used:

| Module | Coverage |
|---|---|
| `sportsdataverse.nba` / `.wnba` | NBA / WNBA (+ stats endpoints) |
| `sportsdataverse.mbb` / `.wbb` | NCAA M/W basketball |
| `sportsdataverse.cfb` | college football |
| `sportsdataverse.nfl` | NFL (includes nflverse-style loaders) |
| `sportsdataverse.mlb` | MLB Stats API + Savant/Statcast helpers |
| `sportsdataverse.nhl` / `.pwhl` | hockey |
| `sportsdataverse.soccer` | soccer leagues via ESPN-parameterized paths |
| `sportsdataverse.odds` | odds helpers |

**R sisters (deeper in places):** hoopR, wehoop, cfbfastR, baseballr, fastRhockey, oddsapiR, etc.

Site: [sportsdataverse.org/packages](https://www.sportsdataverse.org/packages)

### 3) Baseball specialists

| Package | Notes |
|---|---|
| [pybaseball](https://github.com/jldbc/pybaseball) | Python: Statcast/Savant, FanGraphs, Baseball Reference style pulls |
| baseballr | R sister in SportsDataverse orbit |
| collegebaseball | NCAA baseball (Python) |

### 4) Soccer specialists

| Package / source | Notes |
|---|---|
| statsbombpy | StatsBomb open data + API patterns |
| sportsdataverse.soccer | ESPN-parameterized league access |
| nwslpy / nwslR | NWSL |
| FBref / Understat ecosystems | common public sources; respect ToS/rate limits |

### 5) Odds / markets

| Package / source | Notes |
|---|---|
| oddsapiR / The Odds API | keyed API; not fully free unlimited |
| sportsdataverse.odds | SDV odds helpers |
| book/exchange exports | user-provided panels → `market-data-hygiene` |

Market claims still require `clv-evaluation` after clean panels.

## Recommended Python stack (default for this repo)

Core analytics:

```text
python >= 3.10
pandas
polars
numpy
scipy
scikit-learn
statsmodels
pyarrow
matplotlib
```

Sports data loaders (install what you need):

```text
nflreadpy          # NFL first-class
sportsdataverse    # multi-sport
pybaseball         # MLB depth
# optional:
# statsbombpy
# soccerdata (if maintained/needed)
```

Tooling:

```text
uv or pip
jupyter or plain scripts
pytest (if extending package skills/scripts)
```

R users can mirror with nflreadr + SportsDataverse R packages; package skills here are Python-first unless noted.

## What agents must still do after loading data

1. Declare prediction timestamp T (`feature-rules`)
2. Build time-safe features
3. Choose baselines (`baseline-models`)
4. Lock validation (`validation-design`)
5. Audit leakage (`leakage-audit`)
6. Only then claim results (`doctrine` / `model-card`)

Loading PBP is not an edge.

## Source reliability posture

| Source class | Posture |
|---|---|
| nflverse releases | high trust for public NFL research |
| SportsDataverse loaders | high utility; verify endpoint freshness |
| Scrapers (Reference/FanGraphs/etc.) | fragile; cache; expect breakage |
| Paid/keyed odds APIs | fine if disclosed; not required for paper claims |
| Unlicensed dumps | do not teach as default |

## Related skills in this repo

- `environment-setup` — install/runtime checklist
- `data-sources` — choose a source for a question
- `nflreadpy` — NFL loader workflows
- `sportsdataverse-py` — multi-sport loader workflows
- `pybaseball` — MLB loader workflows
