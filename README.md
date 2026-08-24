# Sports Analytic Skills

Agent skills for **sports modeling and analytics** — deep operator manuals, sports-specific workflows, reference docs, and runnable Python scripts. Works with any agent that supports the [Agent Skills](https://agentskills.io/) standard. Also ships as an [Agent Plugins](https://agent-plugins.org/) package (`plugin.json` + `skills/`).

The skills drive a real Python toolkit (`sports_ds`) on public sports data (nflverse, SportsDataverse, pybaseball, and more).

---

## Getting started

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills

python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# verify
pytest -q
sports-ds nfl-eda --seasons 2024
```

Install the skills into an agent host:

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

Optional multi-sport loaders:

```bash
pip install -e ".[multi]"
```

---

## What this is

A sports data science skill pack for agents and humans:

| Layer | Role |
|---|---|
| `skills/<name>/SKILL.md` | Full topic manual: when to use, workflow, code, reporting |
| `skills/<name>/references/` | Deep method detail |
| `skills/<name>/scripts/` | Runnable sports helpers agents can execute |
| `src/sports_ds/` | Installable package: load → EDA → features → model → validate |
| `sports-ds` CLI | One-command workflows on real data |

Each skill is built so an agent can run a full analysis path without inventing method from scratch.

---

## What's included

### Foundation
| Skill | Purpose |
|---|---|
| [sports-modeling-doctrine](skills/sports-modeling-doctrine/) | Question, baselines, time order, success metrics |
| [environment-setup](skills/environment-setup/) | Install and verify toolkit + scripts |
| [data-sources](skills/data-sources/) | Choose public sports data ecosystems |

### Data loaders
| Skill | Purpose |
|---|---|
| [nflreadpy](skills/nflreadpy/) | NFL via nflverse / team-game panels |
| [sportsdataverse-py](skills/sportsdataverse-py/) | Multi-sport SportsDataverse loads |
| [pybaseball](skills/pybaseball/) | MLB Statcast and season tables |

### EDA and presentation
| Skill | Purpose |
|---|---|
| [eda-sports](skills/eda-sports/) | Sports-panel EDA before modeling |
| [sports-visualization](skills/sports-visualization/) | Honest sports figures |
| [anti-slop-analytics](skills/anti-slop-analytics/) | Kill chartjunk and fake certainty |

### Modeling
| Skill | Purpose |
|---|---|
| [feature-rules](skills/feature-rules/) | Time-safe pre-game features |
| [time-series-sports](skills/time-series-sports/) | Rolling / EWMA form |
| [baseline-models](skills/baseline-models/) | Strong simple baselines first |
| [statistical-modeling](skills/statistical-modeling/) | GLMs, diagnostics, effect sizes, hierarchical models |
| [predictive-modeling](skills/predictive-modeling/) | ML under season walk-forward validation |
| [ratings-strength-models](skills/ratings-strength-models/) | Elo / power ratings |

### Validation and simulation
| Skill | Purpose |
|---|---|
| [validation-design](skills/validation-design/) | Season walk-forward and metric locks |
| [leakage-audit](skills/leakage-audit/) | Look-ahead / target leakage review |
| [calibration-check](skills/calibration-check/) | Probability reliability |
| [simulation-sports](skills/simulation-sports/) | Monte Carlo season / matchup projections |

### Reporting
| Skill | Purpose |
|---|---|
| [model-interpretation](skills/model-interpretation/) | Drivers, error slices, failure modes |
| [results-reporting](skills/results-reporting/) | Clear write-ups with baselines |
| [model-card](skills/model-card/) | Durable model documentation |
| [experiment-log](skills/experiment-log/) | Reproducible experiment records |

---

## How a full analysis runs

```text
doctrine
  → pick source + load data
  → EDA
  → time-safe features (form / ratings)
  → baselines
  → statistical model and/or ML
  → walk-forward validation + leakage audit + calibration
  → interpret → report / model card / experiment log
```

### CLI examples

```bash
sports-ds nfl-eda --seasons 2023-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
```

### Skill script examples

```bash
python skills/eda-sports/scripts/panel_report.py --seasons 2023-2024
python skills/statistical-modeling/scripts/glm_diagnostics.py --seasons 2018-2023
python skills/baseline-models/scripts/run_baselines.py --seasons 2018-2024
python skills/ratings-strength-models/scripts/elo_asof.py --seasons 2018-2024
python skills/calibration-check/scripts/calibration_report.py --seasons 2018-2024
python skills/leakage-audit/scripts/audit_pregame_features.py --seasons 2023-2024
```

---

## Package layout

```text
src/sports_ds/
  data/           # loaders (nflverse first)
  eda/            # panel summaries
  features/       # shifted pre-game form features
  models/         # baselines + classifiers
  validation/     # season walk-forward splits
  pipelines/      # end-to-end NFL win model
  cli.py
skills/           # agent skills (SKILL.md + references + scripts)
tests/
docs/
```

---

## Design rules

1. Sports modeling first — wins, margins, counts, ratings, form, simulation, reporting.
2. Time safety — pre-game features must be knowable at decision time T.
3. Walk-forward validation over random game shuffles for season sports.
4. Baselines before complexity.
5. Skills drive real code (`sports_ds` + bundled scripts).
6. Multi-sport core; NFL is the first fully wired pipeline.

---

## Docs

- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [Getting started](./docs/getting-started.md)
- [Skill authoring](./docs/skill-authoring.md)
- [Skill taxonomy](./docs/taxonomy.md)
- [Data ecosystem](./docs/data-ecosystem.md)
- [Environment](./docs/environment.md)
- [Contributing](./CONTRIBUTING.md)

---

## License

MIT
