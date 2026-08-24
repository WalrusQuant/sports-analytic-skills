---
name: environment-setup
description: >
  Install and verify the sports_ds sports data science system across NFL and
  multi-sport paths. Use when setting up a new machine, onboarding an agent, or
  checking that loaders, tests, CLI pipelines, and skill scripts all run — even
  if the user only says "it doesn't import" or "set this up." Includes verify
  scripts, multi-sport extras, and troubleshooting.
version: "0.5.0"
license: MIT
metadata:
  version: "0.5.0"
---

# Environment Setup

## Overview

Get a clean Python environment that can run:

- the `sports_ds` package (`0.9+`)
- `sports-ds` CLI (NFL + NBA/MLB pipelines)
- tests
- skill scripts against public sports data

---

## When to Use This Skill

Use when:

- First clone of the repo
- Agent needs a working runtime before modeling
- “It doesn’t import” / CLI missing / tests fail
- Verifying skill scripts after install
- Enabling multi-sport extras (`[multi]`)

Do **not** use when:

- Choosing which data source → `data-sources`
- Debugging a single model fold → modeling skills

---

## Install

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e .
```

Optional multi-sport extras (NBA/MLB loaders via SportsDataverse/pybaseball):

```bash
pip install -e ".[multi]"
```

Optional richer classical stats / plots:

```bash
pip install "pingouin>=0.6" seaborn
```

Dev/tests:

```bash
pip install -e ".[dev]"
# or with multi:
pip install -e ".[multi,dev]"
```

---

## Verify (in order)

```bash
# 1. unit tests
pytest -q

# 2. package import + tiny load + ratings/audit modules
python skills/environment-setup/scripts/verify_install.py

# 3. feature registry prints
sports-ds feature-registry | head

# 4. NFL CLI happy path
sports-ds nfl-eda --seasons 2024
sports-ds leakage-audit --seasons 2024
sports-ds nfl-win-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds nfl-margin-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds nfl-elo --seasons 2023-2024 --min-train-seasons 1

# 5. multi-sport (requires [multi])
sports-ds nba-eda --seasons 2024
sports-ds mlb-eda --seasons 2024
sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-win-pipeline --seasons 2023-2024 --min-train-seasons 1

# 6. representative skill scripts
python skills/predictive-modeling/scripts/leakage_smoke.py
python skills/eda-sports/scripts/panel_report.py --seasons 2024
python skills/ratings-strength-models/scripts/eval_elo_baseline.py --seasons 2023-2024 --min-train-seasons 1
```

Expected:

- pytest passes (13+ tests)
- verify script prints `OK`
- EDA prints row/game/team summary
- leakage audit returns `CLEAN`
- multi-sport commands work only after `[multi]` install

Checklist: `references/verify_checklist.md`

---

## Runtime Notes

- First nflverse / SDV download needs network
- Data caches via nflreadpy / SDV caches
- Python 3.10+ recommended
- Disk: multi-season extracts can be hundreds of MB+
- Multi-sport is optional; NFL path works with base install

---

## Troubleshooting

| Symptom | Check |
|---|---|
| `sports-ds: command not found` | venv active? `pip install -e .` |
| `ModuleNotFoundError: sports_ds` | install editable from repo root |
| nflverse download errors | network; retry; nflreadpy version |
| `MultiSportDataError` / sportsdataverse missing | `pip install -e ".[multi]"` |
| empty seasons | active season incomplete or bad season list |
| skill script import errors | run from repo root with venv active |
| seaborn/pingouin missing | optional installs above |
| NBA/MLB CLI fails after base install only | install `[multi]` |

More: `references/troubleshooting.md`

---

## Agent Install (skills)

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

Skills live under `skills/<name>/SKILL.md` with `scripts/` and `references/`.

---

## Hard Constraints

1. Verify from repo root with the project venv.
2. Do not claim multi-sport works without `[multi]`.
3. Prefer package CLI over ad-hoc notebooks for smoke checks.
4. Keep secrets out of env files committed to git.

---

## Output Contract

Done means:

- [ ] `pytest -q` green
- [ ] `verify_install.py` prints OK
- [ ] at least one NFL CLI pipeline runs
- [ ] multi-sport path stated as installed or skipped
- [ ] any remaining blockers named

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
pip install -e ".[multi,dev]"
python skills/environment-setup/scripts/verify_install.py
pytest -q
sports-ds feature-registry | head
sports-ds nfl-eda --seasons 2024
sports-ds nfl-elo --seasons 2023-2024 --min-train-seasons 1
sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-margin-pipeline --seasons 2023-2024 --min-train-seasons 1
```
