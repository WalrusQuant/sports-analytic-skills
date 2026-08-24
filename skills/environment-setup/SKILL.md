---
name: environment-setup
description: >
  Install and verify the sports_ds sports data science system and skill
  scripts. Use when setting up a new machine, onboarding an agent, or checking
  that nflverse loads, tests, CLI pipelines, and skill scripts all run.
version: "0.3.0"
license: MIT
metadata:
  version: "0.3.0"
---

# Environment Setup

## Overview

Get a clean Python environment that can run the package, CLI, tests, and skill scripts against public sports data.

## When to Use This Skill

- First clone of the repo
- Agent needs a working runtime before modeling
- “It doesn’t import” / CLI missing / tests fail
- Verifying skill scripts after install

---

## Install

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

Optional multi-sport extras:

```bash
pip install -e ".[multi]"
```

Optional richer classical stats / plots:

```bash
pip install "pingouin>=0.6" seaborn
```

---

## Verify (in order)

```bash
# 1. unit tests
pytest -q

# 2. package CLI EDA
sports-ds nfl-eda --seasons 2024

# 3. package CLI model pipeline (longer; network + CPU)
sports-ds nfl-win-pipeline --seasons 2018-2024

# 4. representative skill scripts
python skills/predictive-modeling/scripts/leakage_smoke.py
python skills/eda-sports/scripts/panel_report.py --seasons 2024
python skills/leakage-audit/scripts/audit_pregame_features.py --seasons 2023-2024
```

Expected:

- pytest passes
- EDA prints row/game/team summary
- pipeline prints walk-forward metrics vs baseline
- leakage smoke / audit return OK/CLEAN

---

## Runtime Notes

- First nflverse download needs network
- Data caches via nflreadpy (see its env vars if you need a custom cache dir)
- Python 3.10+ recommended
- Disk: multi-season NFL extracts can be hundreds of MB+

---

## Troubleshooting

| Symptom | Check |
|---|---|
| `sports-ds: command not found` | venv active? `pip install -e .` |
| `ModuleNotFoundError: sports_ds` | install editable from repo root |
| nflverse download errors | network; retry; check nflreadpy version |
| empty seasons | active season incomplete or bad season list |
| skill script import errors | run from repo root with venv active |

---

## Agent Install (skills)

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

Skills live under `skills/<name>/SKILL.md` with `scripts/` and `references/`.

---

## Related Skills

- Data choice: `data-sources`
- NFL load: `nflreadpy`
- Multi-sport: `sportsdataverse-py`, `pybaseball`
- First analysis: `eda-sports`, `sports-modeling-doctrine`
