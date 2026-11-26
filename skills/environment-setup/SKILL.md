---
name: environment-setup
description: >
  Install this skill pack, connect the sports-leader connector, and optionally
  prepare a user-owned Python environment for notebooks that read Parquet.
  Use for onboarding and setup checks. This repository has no package to install.
license: MIT
metadata:
  version: "1.0.0"
---

# Environment Setup

## Outcome

The skills are installed, the data path is either the sports-leader connector or the public sportsleader-data manifest, and any notebook stack the user asked for imports. Nothing in this repository is installed as a Python package.

Read [verify_checklist.md](references/verify_checklist.md) while checking a new machine and [troubleshooting.md](references/troubleshooting.md) when a step fails.

## When to use this skill

Use it when:

- installing the pack into an agent;
- connecting sports-leader data tools;
- a notebook cannot read a Parquet file the user already downloaded.

Do not use it to choose a dataset (`data-sources`) or to start EDA (`eda-sports`).

| Need | Go instead |
|---|---|
| Which file to read | `data-sources` |
| Analysis | the modeling skill for that question |

## Install the skills

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

One skill, without a prompt:

```bash
npx skills add WalrusQuant/sports-analytic-skills --skill data-sources -y
```

The whole pack:

```bash
npx skills add WalrusQuant/sports-analytic-skills --all
```

A local checkout can be listed with `npx skills add . --list`. Expect 20 skills.

## Connect data

1. If the sports-leader connector is already enabled, use it. In Cursor that connector may be named `sports-leader-v05`. The server source is https://github.com/WalrusQuant/sports-leader-mcp
2. Confirm history with `get_data_status`. It reads the public manifest.
3. If the connector is not connected, read https://github.com/WalrusQuant/sportsleader-data/releases/download/manifest/manifest.json and the Parquet `url` on the chosen entry. `data-sources` has the dataset list.

The connector needs no ESPN key for the public export. Do not put tokens, hosts, or account secrets into a skill file or a commit.

## Optional notebook stack

Only if the user wants to read Parquet in their own project:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pandas pyarrow duckdb
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. Use `python -m pip` so the install follows the active interpreter. Do not modify the system Python. Do not install a package named after this repository. There is not one.

## Verification

1. Record the agent and that `npx skills add` completed.
2. Record whether `sports-leader-v05` (or the sports-leader connector under another client name) is connected.
3. Call `get_data_status`, or fetch the manifest and record `generated_at` and the number of `files`.
4. If the user asked for local Python, import `pandas` and `duckdb` and read one Parquet `url` from the manifest with the snippet in `data-sources`.
5. Stop at the first unexplained failure.

## Reproducibility

Record the skill-pack version (`1.0.0`), the connector name, the manifest `generated_at`, and the file `sha256` values the analysis used. For a notebook, also record the Python version and the package versions. That is the environment record. This repository has no lockfile for a toolkit.
