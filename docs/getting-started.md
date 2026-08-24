# Getting started

## Install the system

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run real workflows

```bash
# EDA on NFL team-game panel
sports-ds nfl-eda --seasons 2023-2024

# End-to-end walk-forward win model
sports-ds nfl-win-pipeline --seasons 2018-2024
```

## What just happened

`nfl-win-pipeline` will:

1. pull NFL schedules via nflverse/`nflreadpy`
2. build team-game rows
3. summarize the panel
4. create pre-game form features only (shifted, no future)
5. walk-forward by season
6. score constant baseline vs logistic vs hist GBM

## Agent skills

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

Skills tell an agent how to operate this package. The package is the system.

## Tests

```bash
pytest -q
```
