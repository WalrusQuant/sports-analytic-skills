---
name: environment-setup
description: >
  Install and verify the sports_ds sports data science system.
version: "0.2.0"
license: MIT
---

# Environment Setup

## Install

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pytest -q
sports-ds nfl-eda --seasons 2024
```

Optional multi-sport extras:

```bash
pip install -e ".[multi]"
```

## Verify

- `pytest -q` passes
- `sports-ds nfl-eda --seasons 2024` prints a panel summary
- `sports-ds nfl-win-pipeline --seasons 2018-2024` runs walk-forward metrics

## Notes

- Requires network first time for nflverse downloads
- Cache controlled by nflreadpy env vars if needed
