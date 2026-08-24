# Sports Analytic Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.5.0-blue.svg)](plugin.json)
[![Skills](https://img.shields.io/badge/Skills-23_drafted-brightgreen.svg)](#available-skills)
[![Status](https://img.shields.io/badge/Status-sports_data_science-orange.svg)](#project-status)
[![Standard](https://img.shields.io/badge/Standard-Agent_Skills-blueviolet.svg)](https://agentskills.io/)
[![Plugins](https://img.shields.io/badge/Standard-Agent_Plugins-0A7A72.svg)](https://agent-plugins.org/)

> Agent skills for **sports data science**: load data, explore it, model it, predict, simulate, and explain results.

**Sports Analytic Skills** is an open Agent Skills library for multi-sport analysis and prediction. It is for building models and doing analysis — not betting products, odds cleaning, EV systems, or arbitrage.

Compatible with Agent Skills hosts (Claude Code, Codex, Cursor, OpenClaw, and others).

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

---

## Project status

| Item | State |
|---|---|
| Version | 0.5.0 |
| Focus | Sports data science (modeling, prediction, analysis) |
| Skills drafted | **23** |
| Skills ready | 0 (all still `draft`) |
| Repo | https://github.com/WalrusQuant/sports-analytic-skills |

---

## What this is

Skills that help an AI agent do sports data science:

- **Data I/O** — nflverse, SportsDataverse, pybaseball, environment setup
- **EDA & visualization** — coverage, distributions, honest figures
- **Statistical modeling** — GLMs, hierarchical structure, uncertainty
- **Machine learning / prediction** — baselines → ML under time-safe validation
- **Ratings & form** — strength models, rolling form, time series
- **Simulation** — game/season projection from models
- **Interpretation & reporting** — explain drivers, write results
- **Validation for sports chronology** — leakage checks, walk-forward evaluation

### What this is not

- Odds cleaning pipelines
- EV betting systems
- Arbitrage tools
- Tip services / pick generators
- Bankroll products

If a task is “get lines, clean vig, find +EV,” this pack is the wrong tool.

---

## Available skills

### Catalog summary

| Domain | Count | Skills |
|---|---:|---|
| Foundation | 1 | sports-modeling-doctrine |
| Data plane | 5 | environment-setup, data-sources, nflreadpy, sportsdataverse-py, pybaseball |
| EDA & viz | 3 | eda-sports, sports-visualization, anti-slop-analytics |
| Modeling | 6 | baseline-models, statistical-modeling, predictive-modeling, ratings-strength-models, time-series-sports, feature-rules |
| Validation | 3 | validation-design, leakage-audit, calibration-check |
| Simulation | 1 | simulation-sports |
| Interpretation & reporting | 3 | model-interpretation, model-card, results-reporting |
| Ops | 1 | experiment-log |
| **Total** | **23** | |

### Data plane

| Skill | Path |
|---|---|
| environment-setup | [`skills/environment-setup`](./skills/environment-setup/SKILL.md) |
| data-sources | [`skills/data-sources`](./skills/data-sources/SKILL.md) |
| nflreadpy | [`skills/nflreadpy`](./skills/nflreadpy/SKILL.md) |
| sportsdataverse-py | [`skills/sportsdataverse-py`](./skills/sportsdataverse-py/SKILL.md) |
| pybaseball | [`skills/pybaseball`](./skills/pybaseball/SKILL.md) |

### Analysis & modeling

| Skill | Path |
|---|---|
| sports-modeling-doctrine | [`skills/sports-modeling-doctrine`](./skills/sports-modeling-doctrine/SKILL.md) |
| eda-sports | [`skills/eda-sports`](./skills/eda-sports/SKILL.md) |
| feature-rules | [`skills/feature-rules`](./skills/feature-rules/SKILL.md) |
| baseline-models | [`skills/baseline-models`](./skills/baseline-models/SKILL.md) |
| statistical-modeling | [`skills/statistical-modeling`](./skills/statistical-modeling/SKILL.md) |
| predictive-modeling | [`skills/predictive-modeling`](./skills/predictive-modeling/SKILL.md) |
| ratings-strength-models | [`skills/ratings-strength-models`](./skills/ratings-strength-models/SKILL.md) |
| time-series-sports | [`skills/time-series-sports`](./skills/time-series-sports/SKILL.md) |
| simulation-sports | [`skills/simulation-sports`](./skills/simulation-sports/SKILL.md) |
| model-interpretation | [`skills/model-interpretation`](./skills/model-interpretation/SKILL.md) |

### Validation & reporting

| Skill | Path |
|---|---|
| validation-design | [`skills/validation-design`](./skills/validation-design/SKILL.md) |
| leakage-audit | [`skills/leakage-audit`](./skills/leakage-audit/SKILL.md) |
| calibration-check | [`skills/calibration-check`](./skills/calibration-check/SKILL.md) |
| sports-visualization | [`skills/sports-visualization`](./skills/sports-visualization/SKILL.md) |
| anti-slop-analytics | [`skills/anti-slop-analytics`](./skills/anti-slop-analytics/SKILL.md) |
| model-card | [`skills/model-card`](./skills/model-card/SKILL.md) |
| results-reporting | [`skills/results-reporting`](./skills/results-reporting/SKILL.md) |
| experiment-log | [`skills/experiment-log`](./skills/experiment-log/SKILL.md) |

### Typical workflow

```text
environment-setup
  → data-sources → nflreadpy | sportsdataverse-py | pybaseball
  → eda-sports
  → sports-modeling-doctrine
  → feature-rules + baseline-models
  → statistical-modeling | ratings-strength-models | predictive-modeling
  → validation-design + leakage-audit
  → calibration-check (if probabilities)
  → model-interpretation + sports-visualization
  → simulation-sports (optional)
  → results-reporting + model-card + experiment-log
```

---

## Install

### Skills into an agent host

```bash
npx skills add WalrusQuant/sports-analytic-skills
npx skills add WalrusQuant/sports-analytic-skills --skill predictive-modeling
```

### Python data stack (for loaders/modeling code)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/python-data.txt
python skills/nflreadpy/scripts/smoke_load.py
```

Details: [docs/environment.md](./docs/environment.md), [docs/data-ecosystem.md](./docs/data-ecosystem.md), [docs/getting-started.md](./docs/getting-started.md)

---

## Architecture

```text
Modeling & analysis skills
  EDA, stats, ML, ratings, form, simulation, interpretation

Data plane
  environment, source choice, nflverse/SDV/pybaseball loaders + scripts

Supporting validation
  time-safe splits, leakage checks, calibration, experiment logs
```

Deep dive: [ARCHITECTURE.md](./ARCHITECTURE.md)

---

## Docs

| Doc | Purpose |
|---|---|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | system design |
| [docs/data-ecosystem.md](./docs/data-ecosystem.md) | nflverse / SportsDataverse / pybaseball map |
| [docs/environment.md](./docs/environment.md) | install surface |
| [docs/getting-started.md](./docs/getting-started.md) | install + first use |
| [docs/skill-authoring.md](./docs/skill-authoring.md) | how to write skills |
| [docs/roadmap.md](./docs/roadmap.md) | sequencing |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | contribution bar |

---

## License

MIT. See [LICENSE](./LICENSE).

This project is methodology and tooling guidance for sports data science. It is not betting advice.
