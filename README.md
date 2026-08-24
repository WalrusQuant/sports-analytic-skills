# Sports Analytic Skills

Standalone agent skills for sports analytics and modeling.

Install the skills, point your agent at your data, and use focused guidance for
EDA, time-safe features, baselines, statistical and predictive models,
walk-forward validation, calibration, simulation, interpretation, and honest
reporting. The skills work without this repository's Python package or pipelines.

The repository also contains an optional `sports_ds` toolkit for acquiring and
normalizing public NFL, NBA, and MLB data. The `sports-ds-bridge` skill connects
that toolkit to the portable artifacts consumed by the standalone skills.

## Install the skills

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

That is enough to use the skills. You do not need to clone this repository,
install `sports_ds`, or run an end-to-end pipeline.

Ask your agent to:

- explore a team-game or player-game dataset before modeling;
- audit candidate features for decision-time leakage;
- establish constant and domain baselines;
- build a time-ordered validation design;
- assess probability calibration;
- interpret the largest misses and error slices;
- simulate outcomes from a schedule and win probabilities;
- write a results report or model card.

Each skill documents the input columns or artifact shape it needs. Bundled
helpers operate on user-owned CSV, Parquet, or JSON files and public Python
dependencies; they do not import `sports_ds`.

## A composable analysis path

The skills are independently invocable. Combine only the ones the task needs:

```text
question and decision time
  -> data acquisition
  -> EDA
  -> time-safe features / ratings
  -> baselines and candidate models
  -> time-ordered validation
  -> leakage and calibration checks
  -> interpretation, simulation, and reporting
```

Examples:

```text
Use eda-sports to inspect this CSV at team-game grain. Report coverage,
missingness, duplicated game rows, target balance, and modeling red flags.
```

```text
Use feature-rules and leakage-audit on this feature table. Decision time is
kickoff. Identify every column that would not have been knowable then.
```

```text
Use baseline-models, predictive-modeling, and validation-design to compare a
constant baseline with logistic regression under season walk-forward folds.
```

## Finding data

The data skills work directly with public ecosystems:

- `nflreadpy` for nflverse data;
- `sportsdataverse-py` for supported multi-sport sources;
- `pybaseball` for Statcast and MLB tables;
- `data-sources` for choosing a source and grain.

If the user wants the repository's prebuilt loaders, normalized panels, or CLI,
use `sports-ds-bridge`. It owns all optional `sports_ds` integration and hands a
portable artifact back to the standalone skill.

```text
public source -> sports_ds loader (optional) -> CSV/Parquet/JSON
                                            -> standalone skill
```

## Optional `sports_ds` toolkit

The toolkit is useful when you want ready-made public-data adapters, reusable
feature/model components, or reference pipelines. It is a separate opt-in
runtime, not a dependency of the skills.

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

Optional multi-sport loaders:

```bash
pip install -e ".[multi]"
```

Discover the current toolkit surface with:

```bash
sports-ds --help
sports-ds feature-registry
```

Pipeline commands remain useful reference benchmarks. They are documented in
`sports-ds-bridge`, not embedded as prerequisites throughout the generic skills.

## Skills

### Foundation and data

| Skill | Purpose |
|---|---|
| `sports-modeling-doctrine` | Lock the question, target, decision time, baseline, and success criteria |
| `environment-setup` | Prepare a portable analysis environment for the user's project |
| `data-sources` | Choose a public data source and appropriate grain |
| `nflreadpy` | Load NFL data directly from nflverse |
| `sportsdataverse-py` | Load supported multi-sport public data |
| `pybaseball` | Load Statcast and MLB season data |
| `sports-ds-bridge` | Optionally connect the `sports_ds` toolkit to standalone skill artifacts |

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

## Skill structure

```text
skills/<skill-id>/
  SKILL.md
  references/     # conditional detail
  scripts/        # optional standalone helpers
  agents/         # optional UI metadata
```

The path to a bundled script is resolved relative to its `SKILL.md`; instructions
must not assume the user's current directory is this repository.

## Repository architecture

```text
skills/                         primary product; standalone
  sports-ds-bridge/             optional integration boundary

src/sports_ds/                  optional Python toolkit
  data, eda, features, ...      reusable components
  pipelines/                    reference orchestration
  cli.py                        toolkit command surface

tests/                          toolkit + skill-independence tests
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for dependency rules.

## Design rules

1. A skill-only install works without `sports_ds`.
2. Generic skills consume documented user artifacts and public dependencies.
3. Only `sports-ds-bridge` may direct users to the optional toolkit.
4. Predictive features must be knowable at the declared decision time.
5. Time-ordered sports data uses walk-forward validation, not random shuffles by default.
6. Baselines come before model complexity.
7. Reports retain sample sizes, uncertainty, failures, and limitations.

## Development

Repository contributors can install the optional toolkit and test dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

Read [docs/skill-authoring.md](./docs/skill-authoring.md) before changing a skill.

## License

MIT
