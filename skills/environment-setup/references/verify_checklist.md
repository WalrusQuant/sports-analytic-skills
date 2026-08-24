# Environment Verify Checklist

## Base (NFL)

- [ ] Python 3.10+
- [ ] `python -m venv .venv` and activate
- [ ] `pip install -e ".[dev]"`
- [ ] `pytest -q`
- [ ] `python skills/environment-setup/scripts/verify_install.py`
- [ ] `sports-ds feature-registry` prints features
- [ ] `sports-ds nfl-eda --seasons 2024`
- [ ] `sports-ds leakage-audit --seasons 2024` → CLEAN
- [ ] `sports-ds nfl-win-pipeline --seasons 2023-2024 --min-train-seasons 1`
- [ ] `sports-ds nfl-margin-pipeline --seasons 2023-2024 --min-train-seasons 1`
- [ ] `sports-ds nfl-elo --seasons 2023-2024 --min-train-seasons 1`

## Multi-sport optional

- [ ] `pip install -e ".[multi]"`
- [ ] `sports-ds nba-eda --seasons 2024`
- [ ] `sports-ds mlb-eda --seasons 2024`
- [ ] `sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1`
- [ ] `sports-ds mlb-win-pipeline --seasons 2023-2024 --min-train-seasons 1`
- [ ] `sports-ds nba-margin-pipeline --seasons 2023-2024 --min-train-seasons 1`
- [ ] `sports-ds mlb-elo --seasons 2023-2024 --min-train-seasons 1`

## Optional richer stats/plots

- [ ] `pip install pingouin seaborn`
