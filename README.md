# Sports Analytic Skills

**Deep agent skills for sports modeling and analytics.**

A portable skill pack that turns an AI coding agent into a sports data science assistant: load public sports data, explore it, build time-safe features, fit baselines and models, validate out of time, simulate outcomes, and write results honestly.

Works with any host that supports the open [Agent Skills](https://agentskills.io/) standard. Also ships as an [Agent Plugins](https://agent-plugins.org/) package (`plugin.json` + `skills/`). Compatible with Cursor, Claude Code, Codex, and similar agent hosts.

Skills are not thin prompt stubs. Each topic skill is an operator manual with workflows, code, reference material, and runnable scripts. The skills drive a real Python toolkit (`sports_ds`) on public data (nflverse, SportsDataverse, pybaseball, and more).

---

## Table of contents

- [Why use this](#why-use-this)
- [What's included](#whats-included)
- [Getting started](#getting-started)
- [Prerequisites](#prerequisites)
- [Quick examples](#quick-examples)
- [Use cases](#use-cases)
- [How a full analysis runs](#how-a-full-analysis-runs)
- [Available skills](#available-skills)
- [Repository layout](#repository-layout)
- [Design rules](#design-rules)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Why use this

Sports modeling work fails in the same ways over and over:

- features that secretly know the future
- random train/test splits on seasonal games
- models shipped with no baseline
- probability claims with no calibration
- agents inventing method from vibes because the “skill” was a one-page outline

This pack is built to stop that.

| Benefit | What it means in practice |
|---|---|
| **Faster real analysis** | Agent follows a known path: load → EDA → features → baselines → model → validate → report |
| **Time-safe defaults** | Pre-game features and walk-forward validation are first-class, not optional footnotes |
| **Runnable, not rhetorical** | Skills point at `sports_ds` APIs, CLI commands, and bundled scripts |
| **Honest evaluation** | Baselines, leakage audits, and calibration checks are part of the map |
| **Multi-sport core** | NFL is the first fully wired pipeline; the skill map stays multi-sport |

While an agent can use any Python package on its own, these skills give curated workflows and examples that make sports analysis more reliable.

---

## What's included

This repository provides:

1. **23 sports modeling skills** under `skills/`
   - Each skill: `SKILL.md` + `references/` + `scripts/` when applicable
   - Topics span data loading, EDA, features, ratings, statistical modeling, ML, validation, simulation, and reporting

2. **Installable Python toolkit: `sports_ds`**
   - Load NFL schedules / team-game panels (nflverse via nflreadpy)
   - EDA summaries
   - Time-safe pre-game form features
   - Baselines and classifiers
   - Season walk-forward validation
   - End-to-end win model pipeline

3. **CLI entrypoints**
   - `sports-ds nfl-eda`
   - `sports-ds nfl-win-pipeline`

4. **Agent plugin manifest**
   - `plugin.json` for hosts that load skill packs as plugins

---

## Getting started

### Option 1: Install skills into your agent host

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

After install, ask your agent things like:

- “Run EDA on NFL seasons 2018–2024”
- “Build a pre-game win model with walk-forward validation”
- “Audit these features for leakage”
- “Fit a logistic GLM and report odds ratios and calibration”

### Option 2: Clone and use the toolkit locally

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e .
```

Optional multi-sport loaders:

```bash
pip install -e ".[multi]"
```

Optional richer classical stats / plots:

```bash
pip install "pingouin>=0.6" seaborn
```

### Option 3: Agent Plugins (local checkout)

This repo is a valid Agent Plugins package (`plugin.json` + `skills/`).

Point your plugin-capable host at this checkout (host-specific path), reload, and confirm the skills appear.

### Verify the install

```bash
pytest -q
sports-ds nfl-eda --seasons 2024
python skills/environment-setup/scripts/verify_install.py
```

You should see tests pass and a team-game panel summary (rows, teams, home win rate).

---

## Prerequisites

- **Python** 3.10+
- **git**
- **Network** on first nflverse download (data is cached afterward)
- **Agent host** that supports Agent Skills (for skill install) — optional if you only use the Python toolkit
- Disk for parquet/csv caches if you pull multiple seasons

---

## Quick examples

### Explore NFL data

```bash
sports-ds nfl-eda --seasons 2023-2024
python skills/eda-sports/scripts/panel_report.py --seasons 2023-2024 --out data/eda_panel.json
```

### End-to-end walk-forward win model

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024
```

What that does:

1. loads NFL schedules from nflverse
2. builds a team-game panel
3. engineers **pre-game only** form features (shifted, no future leak)
4. walk-forward validates by season
5. compares constant baseline vs logistic vs hist gradient boosting

### Statistical model diagnostics

```bash
python skills/statistical-modeling/scripts/glm_diagnostics.py --seasons 2018-2023
python skills/calibration-check/scripts/calibration_report.py --seasons 2018-2024
```

### Ratings and season simulation

```bash
python skills/ratings-strength-models/scripts/elo_asof.py --seasons 2023-2024 --out data/elo_asof.csv
python skills/simulation-sports/scripts/season_win_sim.py --elo-csv data/elo_asof.csv --season 2024 --n-sims 5000
```

### Leakage audit

```bash
python skills/leakage-audit/scripts/audit_pregame_features.py --seasons 2023-2024
```

### Example agent prompts

**Pre-game NFL win model**

```text
Use the sports analytic skills. Load NFL team-game data for 2018-2024,
run EDA, build time-safe form features, fit baselines and a logistic model,
walk-forward validate by season, check calibration, and write a short results report.
```

**Leakage review**

```text
Audit the sports_ds pre-game feature pipeline for look-ahead leakage.
Report pass/fail findings and what would make the matrix illegal at kickoff.
```

**Ratings baseline**

```text
Build as-of Elo ratings for NFL 2018-2024 and evaluate a logistic model
on elo_diff + home under season walk-forward. Compare to a constant baseline.
```

---

## Use cases

### Game prediction
- Pre-game win probability models
- Margin models
- Baseline ladders before ML complexity
- Walk-forward evaluation by season

### Team and player strength
- Elo / power ratings with strict as-of timing
- Form features (rolling, expanding, EWMA)
- Opponent differentials known before the game

### Validation and trust
- Season walk-forward splits
- Leakage audits on feature matrices
- Probability calibration (ECE, Brier, reliability curves)
- Error slices by season / home-away / probability tails

### Simulation and planning
- Monte Carlo season win totals from rating or probability models
- Uncertainty bands, not only expected wins

### Reporting
- Results writeups with baselines, n, limits, repro commands
- Model cards and experiment logs
- Figure honesty checks (no chartjunk, no baseline erasure)

---

## How a full analysis runs

The pack is a pipeline, not a random pile of files:

```text
1. Lock the question and primary metric          → sports-modeling-doctrine
2. Install / verify runtime                      → environment-setup\n3. Choose public data source                     → data-sources
4. Load data                                     → nflreadpy / sportsdataverse-py / pybaseball
5. Explore                                       → eda-sports, sports-visualization
6. Build time-safe features                      → feature-rules, time-series-sports, ratings-strength-models
7. Fit strong simple baselines                   → baseline-models
8. Fit statistical models and/or ML              → statistical-modeling, predictive-modeling
9. Validate out of time                          → validation-design
10. Audit leakage + calibration                  → leakage-audit, calibration-check
11. Simulate if needed                           → simulation-sports
12. Interpret and report                         → model-interpretation, results-reporting, model-card, experiment-log
13. Clean presentation                           → anti-slop-analytics
```

---

## Available skills

### Foundation
| Skill | Purpose |
|---|---|
| [sports-modeling-doctrine](skills/sports-modeling-doctrine/) | Define the question, baselines, time order, and what “good” means |
| [environment-setup](skills/environment-setup/) | Install and verify toolkit + skill scripts |
| [data-sources](skills/data-sources/) | Choose public sports data ecosystems for the grain you need |

### Data loaders
| Skill | Purpose |
|---|---|
| [nflreadpy](skills/nflreadpy/) | NFL via nflverse; schedules and team-game panels through `sports_ds` |
| [sportsdataverse-py](skills/sportsdataverse-py/) | Multi-sport SportsDataverse loads |
| [pybaseball](skills/pybaseball/) | MLB Statcast and season tables |

### EDA and presentation
| Skill | Purpose |
|---|---|
| [eda-sports](skills/eda-sports/) | Coverage, missingness, targets, leakage scouts before modeling |
| [sports-visualization](skills/sports-visualization/) | Honest sports figures with period, n, baselines |
| [anti-slop-analytics](skills/anti-slop-analytics/) | Kill chartjunk, cropped axes, fake certainty |

### Modeling
| Skill | Purpose |
|---|---|
| [feature-rules](skills/feature-rules/) | Legal pre-game features only (shift / as-of) |
| [time-series-sports](skills/time-series-sports/) | Rolling and EWMA form |
| [baseline-models](skills/baseline-models/) | Constant, home, logistic form baselines first |
| [statistical-modeling](skills/statistical-modeling/) | GLMs, diagnostics, effect sizes, hierarchical structure |
| [predictive-modeling](skills/predictive-modeling/) | ML under season walk-forward validation |
| [ratings-strength-models](skills/ratings-strength-models/) | Elo / power ratings known before the game |

### Validation and simulation
| Skill | Purpose |
|---|---|
| [validation-design](skills/validation-design/) | Season walk-forward folds and metric locks |
| [leakage-audit](skills/leakage-audit/) | Look-ahead and target leakage review |
| [calibration-check](skills/calibration-check/) | Do 30% predictions hit about 30% of the time? |
| [simulation-sports](skills/simulation-sports/) | Monte Carlo win totals and matchup uncertainty |

### Reporting
| Skill | Purpose |
|---|---|
| [model-interpretation](skills/model-interpretation/) | Drivers, error slices, largest misses |
| [results-reporting](skills/results-reporting/) | Writeups with baselines, sample size, limits, repro |
| [model-card](skills/model-card/) | Durable model documentation |
| [experiment-log](skills/experiment-log/) | Reproducible experiment records |

Open any skill at `skills/<name>/SKILL.md`.

---

## Repository layout

```text
sports-analytic-skills/
├── README.md
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── LICENSE
├── plugin.json                 # agent plugin manifest
├── pyproject.toml              # sports_ds package + sports-ds CLI
├── docs/
│   ├── getting-started.md
│   ├── data-ecosystem.md
│   ├── environment.md
│   ├── skill-authoring.md
│   ├── taxonomy.md
│   └── ...
├── skills/                     # one folder per skill
│   ├── statistical-modeling/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── scripts/
│   ├── predictive-modeling/
│   ├── eda-sports/
│   └── ...
├── src/sports_ds/              # installable toolkit
│   ├── data/
│   ├── eda/
│   ├── features/
│   ├── models/
│   ├── validation/
│   ├── pipelines/
│   └── cli.py
├── tests/
└── templates/skill/            # starter template for new skills
```

---

## Design rules

1. **Sports modeling first** — wins, margins, counts, ratings, form, simulation, reporting on public data.
2. **Time safety** — pre-game features must be knowable at decision time T.
3. **Walk-forward validation** — season sports are ordered; random game shuffles usually lie.
4. **Baselines before complexity** — beat constant / home / simple form models before celebrating ML.
5. **Skills drive code** — manuals point at package APIs and bundled scripts.
6. **Multi-sport core** — NFL is the first fully wired pipeline; the skill map is not NFL-only.
7. **Honest reporting** — baselines, sample sizes, limits, and failures stay in the writeup.

---

## Documentation

| Doc | Purpose |
|---|---|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | How the skill pack and toolkit fit together |
| [docs/getting-started.md](./docs/getting-started.md) | Install and first runs |
| [docs/data-ecosystem.md](./docs/data-ecosystem.md) | Public sports data sources |
| [docs/environment.md](./docs/environment.md) | Runtime dependencies |
| [docs/skill-authoring.md](./docs/skill-authoring.md) | How to write skills in this repo |
| [docs/taxonomy.md](./docs/taxonomy.md) | Skill domains and relationships |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Contribution and quality bar |

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

Short version: new skills should ship as full operator manuals with references and scripts where useful, stay time-safe for predictive work, and help a stranger run a real sports analysis path.

---

## License

MIT
