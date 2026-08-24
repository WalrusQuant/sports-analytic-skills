# Sports Analytic Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.5.1-blue.svg)](plugin.json)
[![Skills](https://img.shields.io/badge/Skills-23_drafted-brightgreen.svg)](#available-skills)
[![Standard](https://img.shields.io/badge/Standard-Agent_Skills-blueviolet.svg)](https://agentskills.io/)

> Turn an AI coding agent into a sports data scientist.

Load sports data. Explore it. Build models. Predict. Simulate. Explain results.

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

Repo: https://github.com/WalrusQuant/sports-analytic-skills

---

## What the agent can do

| Area | Skills |
|---|---|
| **Get data** | environment-setup, data-sources, nflreadpy, sportsdataverse-py, pybaseball |
| **Explore** | eda-sports, sports-visualization |
| **Model** | sports-modeling-doctrine, feature-rules, baseline-models, statistical-modeling, predictive-modeling, ratings-strength-models, time-series-sports |
| **Validate** | validation-design, leakage-audit, calibration-check |
| **Simulate** | simulation-sports |
| **Explain & ship** | model-interpretation, results-reporting, model-card, experiment-log, anti-slop-analytics |

### Workflow

```text
setup env → load data (nflverse / SportsDataverse / pybaseball)
  → EDA
  → features + baselines
  → stats / ratings / ML models
  → time-safe validation
  → interpret + visualize
  → simulate (optional)
  → report
```

---

## Skills

### Data

| Skill | Path |
|---|---|
| environment-setup | [skills/environment-setup](./skills/environment-setup/SKILL.md) |
| data-sources | [skills/data-sources](./skills/data-sources/SKILL.md) |
| nflreadpy | [skills/nflreadpy](./skills/nflreadpy/SKILL.md) |
| sportsdataverse-py | [skills/sportsdataverse-py](./skills/sportsdataverse-py/SKILL.md) |
| pybaseball | [skills/pybaseball](./skills/pybaseball/SKILL.md) |

### Analysis & modeling

| Skill | Path |
|---|---|
| sports-modeling-doctrine | [skills/sports-modeling-doctrine](./skills/sports-modeling-doctrine/SKILL.md) |
| eda-sports | [skills/eda-sports](./skills/eda-sports/SKILL.md) |
| feature-rules | [skills/feature-rules](./skills/feature-rules/SKILL.md) |
| baseline-models | [skills/baseline-models](./skills/baseline-models/SKILL.md) |
| statistical-modeling | [skills/statistical-modeling](./skills/statistical-modeling/SKILL.md) |
| predictive-modeling | [skills/predictive-modeling](./skills/predictive-modeling/SKILL.md) |
| ratings-strength-models | [skills/ratings-strength-models](./skills/ratings-strength-models/SKILL.md) |
| time-series-sports | [skills/time-series-sports](./skills/time-series-sports/SKILL.md) |
| simulation-sports | [skills/simulation-sports](./skills/simulation-sports/SKILL.md) |
| model-interpretation | [skills/model-interpretation](./skills/model-interpretation/SKILL.md) |

### Validation & reporting

| Skill | Path |
|---|---|
| validation-design | [skills/validation-design](./skills/validation-design/SKILL.md) |
| leakage-audit | [skills/leakage-audit](./skills/leakage-audit/SKILL.md) |
| calibration-check | [skills/calibration-check](./skills/calibration-check/SKILL.md) |
| sports-visualization | [skills/sports-visualization](./skills/sports-visualization/SKILL.md) |
| anti-slop-analytics | [skills/anti-slop-analytics](./skills/anti-slop-analytics/SKILL.md) |
| model-card | [skills/model-card](./skills/model-card/SKILL.md) |
| results-reporting | [skills/results-reporting](./skills/results-reporting/SKILL.md) |
| experiment-log | [skills/experiment-log](./skills/experiment-log/SKILL.md) |

---

## Setup

**Agent skills**

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

**Python stack for data + modeling**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/python-data.txt
python skills/nflreadpy/scripts/smoke_load.py
```

More: [docs/getting-started.md](./docs/getting-started.md) · [docs/data-ecosystem.md](./docs/data-ecosystem.md) · [docs/environment.md](./docs/environment.md)

---

## Docs

| Doc | Purpose |
|---|---|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | design |
| [docs/data-ecosystem.md](./docs/data-ecosystem.md) | nflverse / SportsDataverse / pybaseball |
| [docs/environment.md](./docs/environment.md) | install surface |
| [docs/getting-started.md](./docs/getting-started.md) | first use |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | contributing |

---

## License

MIT. See [LICENSE](./LICENSE).
