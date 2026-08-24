# Skill taxonomy

See also [ARCHITECTURE.md](../ARCHITECTURE.md) §5.

## Locked framing (2026-08-24)

- Name: `sports-analytic-skills`
- L1 = `doctrine` + `ethics` + `risk` (split)
- Core pack is multi-sport and sport-agnostic (NFL/MLB/NBA/NHL/soccer/golf/etc. all in scope later)
- No single sport is the focus of the core
- Modeling is the engine; market dynamics layer in at eval/data joints

## Domains

| Domain | Purpose |
|---|---|
| `core` | Doctrine, ethics, risk framing |
| `modeling` | Baselines, features, model cards |
| `validation` | Splits, walk-forward, leakage, critique |
| `markets` | Odds hygiene, vig, CLV, market eval |
| `ops` | Experiment logging, reproducibility |
| `sport` | Per-sport modules later: NFL, MLB, NBA, NHL, soccer, golf, etc. |
| `comms` | Honest writeups, anti-slop presentation |

## Planned skill IDs

### core (L1)
- `doctrine`
- `ethics`
- `risk`

### modeling (spine)
- `baseline-models`
- `feature-rules`
- `model-card`

### validation
- `leakage-audit`
- `validation-design`
- `backtest-critique`

### markets (layered in)
- `market-data-hygiene`
- `clv-evaluation`
- `calibration-check`

### ops
- `experiment-log`

### comms (later)
- `edge-writeup`
- `anti-slop-analytics`

### sport (later only, multi-sport)
- none until core earns expansion
- equal-class candidates: NFL, MLB, NBA, NHL, soccer, golf, others
- no default “first sport”

Folders under `skills/` stay empty until a skill is actually drafted.
