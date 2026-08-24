# Getting started

## Install

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Optional multi-sport extras:

```bash
pip install -e ".[multi]"
```

## Run package workflows

```bash
sports-ds nfl-eda --seasons 2023-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
sports-ds nfl-margin-pipeline --seasons 2018-2024
sports-ds nfl-elo --seasons 2018-2024
sports-ds calibrate --seasons 2018-2024
sports-ds leakage-audit --seasons 2023-2024
```

- `nfl-win-pipeline` — team win walk-forward (constant / logistic / hist GBM)
- `nfl-margin-pipeline` — point-diff walk-forward (constant / ridge / hist GBR)
- `nfl-elo` — as-of Elo + logistic baseline under walk-forward
- `calibrate` / `leakage-audit` — trust checks on the form feature path
- `nba-eda` / `nba-win-pipeline` — second-sport path (requires `pip install -e ".[multi]"`)

## Run skill scripts

```bash
python skills/eda-sports/scripts/panel_report.py --seasons 2023-2024
python skills/statistical-modeling/scripts/glm_diagnostics.py --seasons 2018-2023
python skills/baseline-models/scripts/run_baselines.py --seasons 2018-2024
python skills/predictive-modeling/scripts/leakage_smoke.py
```

## Agent install

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

Open a skill under `skills/<name>/SKILL.md` and follow its workflow. Scripts live beside each skill.

## Tests

```bash
pytest -q
```
