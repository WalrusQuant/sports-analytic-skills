---
name: environment-setup
description: >
  Install and verify the sports_ds sports data science system and skill
  scripts. Use when setting up a new machine, onboarding an agent, or checking
  that nflverse loads, tests, CLI pipelines, and skill scripts all run — even
  if the user only says "it doesn't import" or "set this up." Includes verify
  scripts and troubleshooting.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# Environment Setup

## Overview

Get a clean Python environment that can run:

- the `sports_ds` package
- `sports-ds` CLI
- tests
- skill scripts against public sports data

---

## When to Use This Skill

Use when:

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

# 2. package import + tiny load
python skills/environment-setup/scripts/verify_install.py

# 3. package CLI EDA
sports-ds nfl-eda --seasons 2024

# 4. representative skill scripts
python skills/predictive-modeling/scripts/leakage_smoke.py
python skills/eda-sports/scripts/panel_report.py --seasons 2024
python skills/leakage-audit/scripts/audit_pregame_features.py --seasons 2023-2024
```

Expected:

- pytest passes
- verify script prints OK
- EDA prints row/game/team summary
- leakage smoke / audit return OK/CLEAN

Checklist: `references/verify_checklist.md`

---

## Runtime Notes

- First nflverse download needs network
- Data caches via nflreadpy (env vars if you need a custom cache dir)
- Python 3.10+ recommended
- Disk: multi-season NFL extracts can be hundreds of MB+

---

## Troubleshooting

| Symptom | Check |
|---|---|
| `sports-ds: command not found` | venv active? `pip install -e .` |
| `ModuleNotFoundError: sports_ds` | install editable from repo root |
| nflverse download errors | network; retry; nflreadpy version |
| empty seasons | active season incomplete or bad season list |
| skill script import errors | run from repo root with venv active |
| seaborn/pingouin missing | optional installs above |

More: `references/troubleshooting.md`

---

## Agent Install (skills)

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

Skills live under `skills/<name>/SKILL.md` with `scripts/` and `references/`.

---

## Bundled Resources

### references/
- `verify_checklist.md`
- `troubleshooting.md`

### scripts/
- `verify_install.py`

---

## Related Skills

- Data choice: `data-sources`
- NFL load: `nflreadpy`
- Multi-sport: `sportsdataverse-py`, `pybaseball`
- First analysis: `eda-sports`, `sports-modeling-doctrine`

---

## Quick Command Card

```bash
pip install -e .
python skills/environment-setup/scripts/verify_install.py
pytest -q
sports-ds nfl-eda --seasons 2024
```
