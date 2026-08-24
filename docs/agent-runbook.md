# Agent runbook

Prompts and command paths that should work after `pip install -e .`.

## Setup

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
# optional NBA path
pip install -e ".[multi]"
pytest -q
```

## Prompt pack (copy/paste)

### 1. EDA
```text
Use sports analytic skills. Run NFL EDA for 2023-2024 and summarize coverage,
home win rate, and any red flags before modeling.
```
Commands:
```bash
sports-ds nfl-eda --seasons 2023-2024
python skills/eda-sports/scripts/panel_report.py --seasons 2023-2024
```

### 2. Win model + baselines
```text
Build a pre-game NFL team win model for 2018-2024 with time-safe form features.
Walk-forward by season. Compare constant, logistic, and hist GBM. Report mean metrics.
```
```bash
sports-ds nfl-win-pipeline --seasons 2018-2024
```

### 3. Margin model
```text
Run the NFL margin (point_diff) walk-forward pipeline for 2018-2024 and report MAE vs constant baseline.
```
```bash
sports-ds nfl-margin-pipeline --seasons 2018-2024
```

### 4. Elo baseline
```text
Build as-of Elo ratings and evaluate elo_diff + home logistic under season walk-forward.
```
```bash
sports-ds nfl-elo --seasons 2018-2024
```

### 5. Trust checks
```text
Audit pre-game form features for leakage and report calibration for the win logistic path.
```
```bash
sports-ds leakage-audit --seasons 2023-2024
sports-ds calibrate --seasons 2018-2024
```

### 6. Writeup
```text
Using the pipeline JSON, write a short results report with baselines, n, limits, and repro commands.
```
```bash
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win_pipeline.json
python skills/results-reporting/scripts/render_pipeline_report.py --json data/nfl_win_pipeline.json
```

### 7. NBA path (optional extra)
```text
If sportsdataverse is installed, run NBA EDA and a win walk-forward for 2023-2024.
```
```bash
sports-ds nba-eda --seasons 2023-2024
sports-ds nba-win-pipeline --seasons 2023-2024
```

## Agent failure checklist

If something fails, check in order:

1. venv active + `pip install -e .`
2. network available for first nflverse download
3. seasons string format: `2018-2024` or `2023,2024`
4. NBA commands require `pip install -e ".[multi]"`
5. run from repo root so skill scripts import `sports_ds`
