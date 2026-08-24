# Sports Analytic Skills

Deep agent skills for **sports modeling and analytics**, plus a Python toolkit (`sports_ds`) the skills operate.

This is a sports-specific skill library in the same *depth* style as serious scientific agent skills: long operator manuals, sports-specific workflows, bundled references, and runnable scripts agents can call.

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

sports-ds nfl-eda --seasons 2023-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
```

Agent install:

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

## What this is

A multi-sport **data science** system for agents and humans:

| Layer | Role |
|---|---|
| `skills/` | Deep topic manuals (EDA, features, stats, ML, validation, ratings, simulation, reporting, loaders) |
| `skills/*/scripts/` | Sports-specific Python helpers agents run |
| `skills/*/references/` | Method detail too long for the main skill file |
| `src/sports_ds/` | Installable package: load → EDA → features → baselines/ML → walk-forward → report |
| `sports-ds` CLI | One-command workflows on real nflverse data |

Skills are not thin prompt stubs. Each topic skill is meant to be detailed enough that an agent can execute a full analysis path without inventing method from scratch.

## Skills

### Data

| Skill | Job |
|---|---|
| `environment-setup` | Install and verify the toolkit |
| `data-sources` | Choose public sports data ecosystems |
| `nflreadpy` | NFL via nflverse / `sports_ds.data.nfl` |
| `sportsdataverse-py` | Multi-sport SportsDataverse loaders |
| `pybaseball` | MLB Statcast and season tables |

### EDA and presentation

| Skill | Job |
|---|---|
| `eda-sports` | Sports-panel EDA before modeling |
| `sports-visualization` | Honest sports figures |
| `anti-slop-analytics` | Kill chartjunk and fake certainty |

### Modeling

| Skill | Job |
|---|---|
| `sports-modeling-doctrine` | Question, baselines, time-order standards |
| `feature-rules` | Time-safe pre-game features |
| `baseline-models` | Strong simple baselines first |
| `statistical-modeling` | GLMs, hierarchical structure, diagnostics |
| `predictive-modeling` | ML under walk-forward validation |
| `ratings-strength-models` | Elo / power ratings / strength |
| `time-series-sports` | Form, rolling windows, recency |

### Validation and simulation

| Skill | Job |
|---|---|
| `validation-design` | Season walk-forward and metric locks |
| `leakage-audit` | Look-ahead / target leakage review |
| `calibration-check` | Probability reliability |
| `simulation-sports` | Monte Carlo game/season projections |

### Reporting

| Skill | Job |
|---|---|
| `model-interpretation` | Drivers, slices, failure modes |
| `model-card` | Durable model documentation |
| `results-reporting` | Clear write-ups with baselines |
| `experiment-log` | Reproducible run log |

## Package layout

```text
src/sports_ds/
  data/           # nflverse loaders, team-game panel
  eda/            # panel summaries
  features/       # shifted pre-game form features
  models/         # baselines + classifiers
  validation/     # season walk-forward splits
  pipelines/      # end-to-end NFL win model
  cli.py
skills/           # deep agent skills + scripts + references
tests/
```

## CLI

| Command | Purpose |
|---|---|
| `sports-ds nfl-eda --seasons 2023-2024` | Load and summarize NFL team-game panel |
| `sports-ds nfl-win-pipeline --seasons 2018-2024` | Walk-forward win model (baseline vs logistic vs GBM) |

Example skill scripts:

```bash
python skills/eda-sports/scripts/panel_report.py --seasons 2023-2024
python skills/feature-rules/scripts/feature_preview.py --seasons 2023-2024
python skills/baseline-models/scripts/run_baselines.py --seasons 2018-2024
python skills/validation-design/scripts/print_folds.py --seasons 2018-2024
python skills/predictive-modeling/scripts/leakage_smoke.py
python skills/statistical-modeling/scripts/glm_diagnostics.py --seasons 2018-2023
```

## Design rules

1. **Sports modeling first** — wins, margins, counts, ratings, form, simulation, reporting.
2. **Time safety** — pre-game features must be knowable at decision time T; walk-forward over random game shuffles.
3. **Baselines before complexity** — constant / home / logistic form before celebrating trees.
4. **Skills drive code** — manuals point at package APIs and bundled scripts, not vibes.
5. **Sport-agnostic core** — NFL is the first concrete pipeline; modules stay multi-sport.

## Docs

- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [docs/getting-started.md](./docs/getting-started.md)
- [docs/data-ecosystem.md](./docs/data-ecosystem.md)
- [docs/environment.md](./docs/environment.md)
- [docs/skill-authoring.md](./docs/skill-authoring.md)

## License

MIT
