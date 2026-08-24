# Getting started

## Install the skills

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

No repository clone or `sports_ds` installation is required.

## Start from the task

Give the agent the question, the decision time for predictive work, and the path
to your CSV, Parquet, or JSON artifact.

```text
Use eda-sports on data/team_games.parquet. Confirm the grain, coverage,
missingness, target balance, and any leakage risks before modeling.
```

```text
Use validation-design on data/features.parquet. The prediction is made at
kickoff; create season walk-forward folds and lock the primary metric.
```

Each skill documents the fields it requires. If the artifact does not meet the
contract, the agent should report the missing fields rather than silently infer
them.

## Run a bundled helper

Resolve the helper path relative to the installed skill's `SKILL.md`, not the
current working directory:

```bash
python <path-to-installed-skill>/scripts/<helper>.py --help
```

Helpers use public dependencies and user-owned artifacts. Install only the
packages required by the selected helper in the user's project environment.

## Need public data?

Use one of the source skills:

- `nflreadpy`
- `sportsdataverse-py`
- `pybaseball`
- `data-sources`

If the user specifically wants the optional `sports_ds` toolkit, use
`sports-ds-bridge`. It materializes a portable artifact and hands it back to
the standalone skill.

## Optional toolkit development

Only users who want the repository's Python toolkit or reference pipelines need
the checkout:

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```
