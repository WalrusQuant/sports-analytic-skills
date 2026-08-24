---
name: environment-setup
description: >
  Set up a Python analysis environment for sports modeling with the common
  open data loaders (nflreadpy, sportsdataverse, pybaseball) and core
  scientific stack. Use before loading sports datasets or running package scripts.
version: "0.1.0"
license: MIT
---

# Environment Setup

Data-plane skill. Gets a machine ready to load public sports data and run
analysis code. Judgment skills do not require this; package skills do.

## When to use

- First time using this repo’s data/package skills
- Imports fail for nflreadpy / sportsdataverse / pybaseball
- Starting a fresh venv for multi-sport modeling
- Agent needs to know what to install before coding

## When not to use

- Reading doctrine/validation methodology only
- Environment already verified
- Choosing which league source to use → `data-sources`

## Required inputs

- OS / Python availability
- Whether network install is allowed
- Which sports are in scope for this session (NFL / multi / MLB / etc.)

## Procedure

1. **Confirm Python**
   - Require 3.10+
   - `python --version`

2. **Create/activate a virtual environment**
   - Prefer project-local `.venv`
   - Do not install sports scrapers into system Python by default

3. **Install the data stack**
   - From repo root:
     - `pip install -r requirements/python-data.txt`
     - or `uv pip install -r requirements/python-data.txt`

4. **Install only needed extras**
   - NFL only: `nflreadpy` + core stack may be enough
   - Multi-sport: add `sportsdataverse`
   - MLB depth: add `pybaseball`
   - Soccer open data: optional `statsbombpy`

5. **Configure caches (recommended)**
   - `export NFLREADPY_CACHE=filesystem`
   - `export NFLREADPY_CACHE_DIR="$HOME/.cache/nflreadpy"`

6. **Run smoke checks**
   - Import check:
     - `python -c "import pandas, polars, sklearn; print('core ok')"`
   - Loader checks if installed:
     - `python skills/nflreadpy/scripts/smoke_load.py`
     - `python skills/sportsdataverse-py/scripts/smoke_load.py`
     - `python skills/pybaseball/scripts/smoke_load.py`

7. **Record environment in experiment logs**
   - Python version
   - package versions (`pip freeze` snippet or selected pins)
   - cache mode

## Hard constraints

- Never assume sports packages are preinstalled
- Never scrape around a loader failure without documenting fragility
- Never commit large raw data dumps to git by default
- Prefer official/open loaders over ad-hoc HTML scrapers
- If offline, require pre-staged parquet/csv snapshots

## Anti-patterns

- **Global pip install** on a shared system Python
- **Install everything forever** when only NFL is needed
- **Silent version drift** between experiments
- **Re-download multi-season PBP every run** with cache off
- **Skipping smoke tests** then debugging “model bugs” that are import/network failures

## Output contract

Done means:

- [ ] Python version confirmed
- [ ] venv activated
- [ ] required packages installed for the session scope
- [ ] smoke imports passed
- [ ] cache settings chosen
- [ ] environment notes ready for `experiment-log`

## Handoffs

- `data-sources` — pick league/source
- `nflreadpy` / `sportsdataverse-py` / `pybaseball` — load data
- `feature-rules` — after data is in memory/on disk
- **Stop** if network/install is blocked and no local snapshots exist

## Worked example

**Scope:** NFL walk-forward modeling on laptop.

```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy pandas polars pyarrow scikit-learn statsmodels matplotlib nflreadpy
export NFLREADPY_CACHE=filesystem
python skills/nflreadpy/scripts/smoke_load.py
```

Then proceed to schedules/PBP loads and validation design.

## References

- `docs/environment.md`
- `docs/data-ecosystem.md`
- `requirements/python-data.txt`
