# Sports Analytic Skills

Turn an AI coding agent into a **sports data science assistant**.

This repo is a pack of deep agent skills for sports modeling and analytics, plus a Python toolkit the skills actually run. An agent that loads these skills can pull public sports data, explore it, build time-safe features, fit baselines and models, validate out of time, and write results up without inventing the method from scratch.

It works with hosts that support the [Agent Skills](https://agentskills.io/) standard (and as an [Agent Plugins](https://agent-plugins.org/) package via `plugin.json`).

---

## Why this exists

Sports analysis work fails in predictable ways:

- features that secretly know the future
- random train/test splits on seasonal data
- models shipped with no baseline
- probability claims with no calibration check
- thin “prompt notes” that don’t tell an agent *how* to run the analysis

This pack is built to stop that. Each skill is an operator manual for one job in the sports modeling workflow, with code paths and scripts an agent can execute on real public data.

---

## What you get

**1. Agent skills** under `skills/`

Every skill folder is meant to stand alone:

- `SKILL.md` — full workflow, decision tables, code, reporting
- `references/` — deeper method notes
- `scripts/` — runnable Python helpers

**2. A Python toolkit** (`sports_ds`)

Installable package the skills drive:

- load NFL schedules / team-game panels (nflverse)
- EDA summaries
- time-safe pre-game form features
- baselines + classifiers
- season walk-forward validation
- end-to-end win model pipeline

**3. A CLI** for the common paths

```bash
sports-ds nfl-eda --seasons 2023-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
```

---

## Getting started

### 1. Clone and install the toolkit

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

Optional multi-sport loaders (SportsDataverse, pybaseball):

```bash
pip install -e ".[multi]"
```

### 2. Verify it works

```bash
pytest -q
sports-ds nfl-eda --seasons 2024
```

You should see a team-game panel summary (rows, teams, home win rate, etc.).

### 3. Install the skills into your agent

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

Or point your host at this repo’s `skills/` directory (host-specific). After install, ask the agent things like:

- “Run EDA on NFL 2018–2024 team-game data”
- “Build a pre-game win model with walk-forward validation”
- “Audit this feature set for leakage”
- “Fit a logistic GLM and report odds ratios and calibration”

---

## How a full analysis is supposed to run

The pack is organized as a pipeline, not a random bag of files:

```text
1. Lock the question and success metric
2. Pick a public data source and load it
3. Explore the panel (coverage, missingness, targets)
4. Build time-safe features (form, ratings, rest)
5. Fit strong simple baselines first
6. Fit statistical models and/or ML
7. Validate with season walk-forward (not random shuffles)
8. Audit leakage and check probability calibration
9. Interpret errors and write results up
```

| Step | Skill(s) |
|---|---|
| Question / standards | `sports-modeling-doctrine` |
| Install / verify | `environment-setup` |
| Choose data | `data-sources` |
| Load NFL / multi-sport / MLB | `nflreadpy`, `sportsdataverse-py`, `pybaseball` |
| Explore | `eda-sports`, `sports-visualization` |
| Features | `feature-rules`, `time-series-sports`, `ratings-strength-models` |
| Baselines | `baseline-models` |
| Models | `statistical-modeling`, `predictive-modeling` |
| Validate | `validation-design`, `leakage-audit`, `calibration-check` |
| Simulate | `simulation-sports` |
| Report | `model-interpretation`, `results-reporting`, `model-card`, `experiment-log` |
| Presentation honesty | `anti-slop-analytics` |

---

## Quick examples

### Explore NFL data

```bash
sports-ds nfl-eda --seasons 2023-2024
python skills/eda-sports/scripts/panel_report.py --seasons 2023-2024
```

### Walk-forward win model (baselines vs ML)

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024
```

This loads nflverse schedules, builds a team-game panel, engineers **pre-game** form features only, and scores constant / logistic / hist-GBM models by season.

### Statistical model diagnostics

```bash
python skills/statistical-modeling/scripts/glm_diagnostics.py --seasons 2018-2023
python skills/calibration-check/scripts/calibration_report.py --seasons 2018-2024
```

### Ratings + season simulation

```bash
python skills/ratings-strength-models/scripts/elo_asof.py --seasons 2023-2024 --out data/elo_asof.csv
python skills/simulation-sports/scripts/season_win_sim.py --elo-csv data/elo_asof.csv --season 2024
```

### Leakage check

```bash
python skills/leakage-audit/scripts/audit_pregame_features.py --seasons 2023-2024
```

---

## Skill catalog

### Foundation
- **sports-modeling-doctrine** — define the question, baselines, time order, and what “good” means before fitting
- **environment-setup** — install and verify the toolkit and skill scripts
- **data-sources** — pick the right public ecosystem for the sport and grain

### Data
- **nflreadpy** — NFL via nflverse; schedules and team-game panels through `sports_ds`
- **sportsdataverse-py** — multi-sport loads (NBA, CFB, NHL, and more)
- **pybaseball** — MLB Statcast and season tables

### EDA and presentation
- **eda-sports** — coverage, missingness, targets, leakage scouts before modeling
- **sports-visualization** — figures that state period, n, and baselines
- **anti-slop-analytics** — kill chartjunk, cropped axes, and fake certainty

### Modeling
- **feature-rules** — legal pre-game features only (shift / as-of)
- **time-series-sports** — rolling and EWMA form
- **baseline-models** — constant, home, logistic form baselines first
- **statistical-modeling** — GLMs, diagnostics, effect sizes, hierarchical structure
- **predictive-modeling** — ML under season walk-forward validation
- **ratings-strength-models** — Elo / power ratings as-of game time

### Validation and simulation
- **validation-design** — walk-forward folds and metric locks
- **leakage-audit** — look-ahead and target leakage review
- **calibration-check** — do 30% predictions hit ~30% of the time?
- **simulation-sports** — Monte Carlo win totals and matchup uncertainty

### Reporting
- **model-interpretation** — drivers, slices, biggest misses
- **results-reporting** — writeups with baselines, n, limits, repro
- **model-card** — durable model documentation
- **experiment-log** — reproducible run records

Open any skill at `skills/<name>/SKILL.md`.

---

## Repository layout

```text
skills/                 # agent skills (one folder per topic)
src/sports_ds/          # installable Python toolkit
  data/                 # loaders
  eda/
  features/
  models/
  validation/
  pipelines/
  cli.py
tests/
docs/
templates/skill/        # starter template for new skills
plugin.json             # agent plugin manifest
pyproject.toml
```

---

## Design rules

1. **Sports modeling first** — wins, margins, counts, ratings, form, simulation, reporting on public data.
2. **Time safety** — if it’s a pre-game model, every feature must be knowable at decision time T.
3. **Walk-forward validation** — season sports are ordered; random game shuffles usually lie.
4. **Baselines before complexity** — beat constant / home / simple form models before celebrating ML.
5. **Skills drive code** — manuals point at `sports_ds` and bundled scripts, not vibes.
6. **Multi-sport core** — NFL is the first fully wired pipeline; the skill map is not NFL-only.

---

## Docs

| Doc | What it’s for |
|---|---|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | How the pack and toolkit fit together |
| [docs/getting-started.md](./docs/getting-started.md) | Install and first runs |
| [docs/data-ecosystem.md](./docs/data-ecosystem.md) | Public sports data sources |
| [docs/environment.md](./docs/environment.md) | Runtime dependencies |
| [docs/skill-authoring.md](./docs/skill-authoring.md) | How to write skills in this repo |
| [docs/taxonomy.md](./docs/taxonomy.md) | Skill domains |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Contribution and quality bar |

---

## License

MIT
