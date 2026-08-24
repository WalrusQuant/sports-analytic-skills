# Architecture — Sports Analytic Skills

**Center of gravity:** sports data science for analysis, modeling, and prediction.

## 1. Goal

An agent-usable skill library so a coding agent can:

1. set up an environment
2. load public sports data (nflverse, SportsDataverse, pybaseball, etc.)
3. explore and visualize it
4. engineer time-safe features
5. fit baselines + statistical/ML models
6. validate over time
7. interpret, simulate, and report

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

They teach agents how to use upstream sports data packages. They do not reimplement them.

## 6. Later

- deeper ML where earned
- sport modules (NFL/MLB/NBA/NHL/soccer/golf/…)
- more package skills when needed
- optional workflow runner that composes skills end-to-end
