# Environment Verify Checklist

- [ ] Python 3.10+
- [ ] `python -m venv .venv` and activate
- [ ] `pip install -e .`
- [ ] `pytest -q`
- [ ] `python skills/environment-setup/scripts/verify_install.py`
- [ ] `sports-ds nfl-eda --seasons 2024`
- [ ] `python skills/predictive-modeling/scripts/leakage_smoke.py`
- [ ] Optional: `pip install -e ".[multi]"` for SportsDataverse/pybaseball
- [ ] Optional: `pip install pingouin seaborn` for richer stats/plots
