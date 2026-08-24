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

## Skill IDs

### core (L1) — drafted
- `doctrine` — draft
- `ethics` — draft
- `risk` — draft

### modeling (spine) — drafted
- `baseline-models` — draft
- `feature-rules` — draft
- `model-card` — draft

### validation — drafted
- `leakage-audit` — draft
- `validation-design` — draft
- `backtest-critique` — draft

### ops — drafted
- `experiment-log` — draft

### markets (layered in) — planned
- `market-data-hygiene`
- `clv-evaluation`
- `calibration-check`

### comms (later)
- `edge-writeup`
- `anti-slop-analytics`

### sport (later only, multi-sport)
- none until core earns expansion
- equal-class candidates: NFL, MLB, NBA, NHL, soccer, golf, others
- no default “first sport”

**Drafted count:** 10  
Market layer and later domains remain planned until written.
