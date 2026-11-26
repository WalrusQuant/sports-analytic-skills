# Sports Analytic Skills

[![Release](https://img.shields.io/github/v/release/WalrusQuant/sports-analytic-skills?display_name=tag)](https://github.com/WalrusQuant/sports-analytic-skills/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-20-brightgreen.svg)](#skills)
[![Agent Skills](https://img.shields.io/badge/standard-Agent_Skills-blueviolet.svg)](https://agentskills.io/)
[![Agent Plugins](https://img.shields.io/badge/standard-Agent_Plugins-0A7A72.svg)](https://agent-plugins.org/)
[![Site](https://img.shields.io/badge/site-GitHub%20Pages-111111.svg)](https://walrusquant.github.io/sports-analytic-skills/)

**Site:** [walrusquant.github.io/sports-analytic-skills](https://walrusquant.github.io/sports-analytic-skills/) · **Docs:** [Getting started](https://walrusquant.github.io/sports-analytic-skills/docs.html)

Twenty agent skills for sports analytics and modeling. Version 1.0.0 is markdown only.

Install the skills, point your agent at [sportsleader-data](https://github.com/WalrusQuant/sportsleader-data), and use the pack for EDA, time-safe features, baselines, statistical and predictive models, walk-forward validation, calibration, simulation, interpretation, and honest reporting.

sportsleader-data publishes Parquet for MLB, NBA, NFL, NHL, college football, and men's college basketball. The file list is the [manifest](https://github.com/WalrusQuant/sportsleader-data/releases/download/manifest/manifest.json). The same files are available through the [sports-leader MCP connector](https://github.com/WalrusQuant/sports-leader-mcp). Current-season files are refreshed nightly. This repository does not ship code that downloads or models them.

## Install

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

One skill:

```bash
npx skills add WalrusQuant/sports-analytic-skills --skill eda-sports -y
```

Every skill:

```bash
npx skills add WalrusQuant/sports-analytic-skills --all
```

You do not need to clone this repository to use the skills.

Ask the agent to:

- lock the question, target, decision time, and baseline;
- choose a sportsleader-data dataset and check its grain;
- audit coverage, missingness, and leakage;
- fit a constant baseline before a heavier model;
- score season walk-forward folds;
- check calibration and the largest misses;
- write a results note or model card.

## Analysis path

```text
question and decision time
  -> data-sources (sportsleader-data)
  -> EDA
  -> time-safe features / ratings
  -> baselines and candidate models
  -> time-ordered validation
  -> leakage and calibration checks
  -> interpretation, simulation, and reporting
```

Examples:

```text
Use data-sources and eda-sports on NFL team-game stats from sportsleader-data
for the 2023 and 2024 seasons. Report grain, coverage, missingness, and
whether scores can support a pre-kickoff win label.
```

```text
Use feature-rules and leakage-audit on this feature table. Decision time is
kickoff. Identify every column that would not have been knowable then.
```

```text
Use baseline-models, predictive-modeling, and validation-design to compare a
constant baseline with logistic regression under season walk-forward folds.
```

## Data

`data-sources` is the default acquisition skill. It reads the manifest and, when the sports-leader connector is connected, the connector's historical tools. Those tools may appear in a client as `sports-leader-v05`.

The Parquet files hold schedules, team boxes, team counting stats, player game logs, and current-season roster, injury, transaction, depth-chart, probable, lineup, and weather extracts, as listed in the manifest. They do not include ratings, forecasts, or betting lines. Ids are ESPN ids. NFL, MLB, and college football season numbers are the year the season starts. NBA, NHL, and men's college basketball season numbers are the year the season ends.

Attribute game data to ESPN and to any other source named on that dataset, and attribute the files to sportsleader-data.

## Skills

### Foundation and data

| Skill | Purpose |
|---|---|
| `sports-modeling-doctrine` | Lock the question, target, decision time, baseline, and success criteria |
| `environment-setup` | Install the pack and connect sportsleader-data |
| `data-sources` | Choose a sportsleader-data dataset and grain |

### Exploration and features

| Skill | Purpose |
|---|---|
| `eda-sports` | Audit coverage, grain, missingness, targets, and modeling red flags |
| `sports-visualization` | Produce honest sports charts with context and uncertainty |
| `anti-slop-analytics` | Remove chartjunk, misleading axes, and unsupported claims |
| `feature-rules` | Design decision-time-legal features |
| `time-series-sports` | Build shifted rolling and EWMA form features |
| `ratings-strength-models` | Build as-of Elo and other strength ratings |

### Modeling and validation

| Skill | Purpose |
|---|---|
| `baseline-models` | Establish constant, home, and simple statistical baselines |
| `statistical-modeling` | Fit GLMs and report diagnostics, effects, and uncertainty |
| `predictive-modeling` | Fit and compare predictive models under honest time splits |
| `validation-design` | Define walk-forward folds and lock metrics |
| `leakage-audit` | Audit look-ahead, target, join, and preprocessing leakage |
| `calibration-check` | Evaluate probability reliability and recalibration needs |
| `simulation-sports` | Simulate seasons or matchups from portable probability inputs |

### Interpretation and reporting

| Skill | Purpose |
|---|---|
| `model-interpretation` | Analyze drivers, slices, and largest misses |
| `results-reporting` | Write reproducible results with baselines, sample size, and limits |
| `model-card` | Record a durable model contract |
| `experiment-log` | Maintain a reproducible experiment history |

## Layout

```text
skills/<skill-id>/
  SKILL.md
  references/
```

Each skill is an operator manual. Runnable work uses sportsleader-data, the sports-leader connector, or files the user already owns. Short code examples in a skill illustrate a step. They do not call a program in this repository.

## Design rules

1. Predictive features must be knowable at the declared decision time.
2. Time-ordered sports data uses walk-forward validation.
3. Baselines come before model complexity.
4. Reports retain sample sizes, uncertainty, failures, and limitations.
5. The manifest is the schema. Do not invent a dataset or a column.
6. This is a research workflow, not a betting product and not a claim of edge.

## Contributing

Skill changes are markdown. Read [CONTRIBUTING.md](./CONTRIBUTING.md) and [docs/skill-authoring.md](./docs/skill-authoring.md).

## Disclaimer

This project provides methodological guidance for sports data science and research. You are solely responsible for how you use it.

## License

MIT
