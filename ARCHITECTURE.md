# Architecture — Sports Analytic Skills

**Status:** v0.5 reset (2026-08-24)  
**Center of gravity:** sports data science for analysis, modeling, and prediction.

## 1. Product definition

Build an agent-usable skill library so a coding agent can:

1. set up an environment
2. load public sports data (nflverse, SportsDataverse, pybaseball, etc.)
3. explore and visualize it
4. engineer time-safe features
5. fit baselines + statistical/ML models
6. validate over time
7. interpret, simulate, and report

**Out of scope as product identity:** odds cleaning, EV betting, arbitrage, tip services, bankroll products.

## 2. Layers

```text
┌──────────────────────────────────────────────┐
│ Analysis & modeling skills                   │
│ EDA, stats, ML, ratings, form, simulation    │
├──────────────────────────────────────────────┤
│ Data plane                                   │
│ env setup, source choice, package loaders    │
├──────────────────────────────────────────────┤
│ Supporting validation / ops                  │
│ walk-forward, leakage, calibration, logs     │
└──────────────────────────────────────────────┘
```

Validation skills support good science. They are not the catalog headline.

## 3. Domain map

| Domain | Skills |
|---|---|
| Foundation | sports-modeling-doctrine |
| Data | environment-setup, data-sources, nflreadpy, sportsdataverse-py, pybaseball |
| EDA/Viz | eda-sports, sports-visualization, anti-slop-analytics |
| Modeling | baseline-models, feature-rules, statistical-modeling, predictive-modeling, ratings-strength-models, time-series-sports |
| Validation | validation-design, leakage-audit, calibration-check |
| Simulation | simulation-sports |
| Reporting | model-interpretation, model-card, results-reporting, experiment-log |

## 4. Default workflow

```text
environment-setup
 → data-sources → loader skill
 → eda-sports
 → sports-modeling-doctrine
 → feature-rules + baseline-models
 → statistical-modeling | ratings-strength-models | predictive-modeling
 → validation-design + leakage-audit
 → model-interpretation + sports-visualization
 → simulation-sports (optional)
 → results-reporting / model-card / experiment-log
```

## 5. Package skill shape

Package skills may include:

- `SKILL.md` workflow
- `scripts/` smoke tests and loaders
- pointers to upstream docs

They do not reimplement nflverse/SDV. They teach agents how to use them.

## 6. Non-goals

- Betting market microstructure as core content
- Guaranteed prediction claims
- Autobet integrations
- One-sport favoritism in the core pack

## 7. Later

- deeper ML (sequence models, tracking) where earned
- sport modules (NFL/MLB/NBA/NHL/soccer/golf/…) with domain constraints
- more package skills (e.g. statsbombpy) when needed
- optional workflow runner that composes skills end-to-end
