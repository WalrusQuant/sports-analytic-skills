# Product Charter — Sports Analytic Skills

## What this is

A portable **sports data science** product:

1. Installable Python toolkit: `sports_ds`
2. Deep agent skills that drive that toolkit
3. Public-data modeling workflows: load → EDA → time-safe features → baselines → models → walk-forward validation → calibration/leakage checks → simulation → report

## Users

- Analysts and builders doing sports modeling on public data
- AI coding agents that need operator manuals + runnable code, not vibes

## In scope (v1)

- Team-game prediction (wins, margins)
- Time-safe features and as-of ratings (Elo)
- Season walk-forward validation
- Leakage audit + probability calibration
- Honest reporting (baselines, n, limits, repro)
- NFL deepest first; one additional sport path
- Multi-sport skill map and loaders

## Out of scope (v1)

- Betting / odds / CLV / bankroll / arbitrage product surfaces
- Paid data vendors as a requirement
- Full player-valuation platform
- Dashboard / SaaS app
- Every league under the sun

## Success criteria (v1)

- `pip install -e .` + verify script green
- pytest covers features, splits, ratings as-of, pipeline smoke
- NFL win + margin + Elo baseline paths via CLI
- leakage audit + calibration available as package/CLI
- skills drive package APIs; no stub-only happy paths
- one non-NFL sport path works end-to-end
- cold agent can complete a documented analysis
- README commands work as written
- tagged release with honest claims

## Non-negotiables

- Time safety at decision time T
- Baselines before complexity
- Walk-forward over random shuffles for seasonal sports
- Additive skill depth; no silent deletes
- Free / open craft product
