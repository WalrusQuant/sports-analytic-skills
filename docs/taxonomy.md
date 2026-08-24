# Skill taxonomy

See also [ARCHITECTURE.md](../ARCHITECTURE.md) and README [Available skills](../README.md#available-skills).

## Locked framing

- Name: `sports-analytic-skills`
- L1 = `doctrine` + `ethics` + `risk`
- Core judgment pack is multi-sport / sport-agnostic
- Modeling is the analytic engine; markets layer in at eval/data joints
- Data plane teaches real public loaders (nflverse, SportsDataverse, pybaseball)

## Domains

| Domain | Purpose | Drafted |
|---|---|---:|
| `core` | Doctrine, ethics, risk | 3 |
| `modeling` | Baselines, features, model cards | 3 |
| `validation` | Splits, walk-forward, leakage, critique | 3 |
| `markets` | Odds hygiene, vig, CLV, calibration | 3 |
| `ops` | Experiment logging | 1 |
| `comms` | Honest writeups, anti-slop | 2 |
| `data` | Environment, sources, package loaders | 5 |
| `sport` | Per-sport modules later | 0 |

## Skill IDs

### core — drafted
- doctrine, ethics, risk

### modeling — drafted
- baseline-models, feature-rules, model-card

### validation — drafted
- leakage-audit, validation-design, backtest-critique

### ops — drafted
- experiment-log

### markets — drafted
- market-data-hygiene, clv-evaluation, calibration-check

### comms — drafted
- edge-writeup, anti-slop-analytics

### data plane — drafted
- environment-setup
- data-sources
- nflreadpy
- sportsdataverse-py
- pybaseball

### later
- statsbombpy / soccer depth
- odds API package skill
- R-side mirrors (nflreadr, hoopR, cfbfastR) if needed
- sport modules (NFL/MLB/NBA/NHL/soccer/golf/etc.)

**Drafted count:** 20
