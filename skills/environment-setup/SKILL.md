---
name: environment-setup
description: >
  Create and verify a portable Python environment for sports analysis. Use for
  machine setup, onboarding, dependency diagnosis, or reproducibility checks.
license: MIT
metadata:
  version: "0.7.0"
---

# Environment Setup

## Outcome

Produce an isolated environment, explicit dependency record, and machine-readable
verification report. Install only the public libraries required by the selected
skills and data sources.

## Inputs

- operating system and Python version
- analysis tasks and named public loaders
- CPU, memory, storage, and network constraints
- required output formats such as Parquet, JSON, or images

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy pandas scipy scikit-learn statsmodels matplotlib pyarrow
```

Install public loaders only when needed:

```bash
python -m pip install nflreadpy
python -m pip install pybaseball
python -m pip install sportsdataverse
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

## Verification order

1. Record `python --version` and `python -m pip --version`.
2. Confirm both commands resolve inside the same environment.
3. Import the minimum scientific packages.
4. Run each selected loader's `--help` or lightweight import probe.
5. Execute one bounded public-data sample if network access is allowed.
6. Write versions and verification status to a user-owned artifact.
7. Freeze dependencies only after the environment succeeds.

```bash
python <path-to-environment-setup>/scripts/verify_install.py
python <path-to-environment-setup>/scripts/verify_install.py --packages numpy,pandas,sklearn --out data/environment.json
python -m pip freeze > requirements-lock.txt
```

## Troubleshooting

| Symptom | Check |
|---|---|
| `ModuleNotFoundError` | active interpreter and exact import name |
| install succeeds but import fails | compare interpreter and installer paths |
| Parquet write fails | install `pyarrow`; verify output permissions |
| loader request fails | network, provider status, rate limits, coverage |
| native-library error | Python architecture and wheel availability |
| stale notebook imports | restart the kernel after installation |

## Hard constraints

- Use an isolated environment; do not modify the system interpreter.
- Use `python -m pip` so installation follows the active interpreter.
- Do not install every loader by default.
- Do not make a network request as part of `--help`.
- Do not hide failed imports or substitute packages silently.
- Record versions and platform information with analysis artifacts.

## Output contract

Report Python version, executable, platform, requested packages, resolved
versions, loader probes, skipped network checks, exact failures, remediations,
and the location of the environment report and dependency lock.

## Resources

- `references/verify_checklist.md` — portable verification checklist
- `references/troubleshooting.md` — common environment failures
- `scripts/verify_install.py` — dependency probe with optional JSON output
