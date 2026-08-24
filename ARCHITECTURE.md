# Architecture

## Product boundary

The primary product is the standalone skill pack under `skills/`. A user can
install those skills into an agent host and apply them to existing data without
cloning this repository or installing its Python package.

`sports_ds` is an optional toolkit in the same repository. It provides public
data loaders, normalized panels, reusable analysis components, a CLI, and
reference pipelines. The `sports-ds-bridge` skill is the only integration point
between that toolkit and the generic skills.

## Dependency direction

```text
user CSV / Parquet / JSON ───────────────> generic skill
public Python data library ──────────────> data-source skill

sports_ds data/core/CLI (optional)
                │
                v
        sports-ds-bridge
                │ portable artifact
                v
          generic skill

sports_ds pipelines ──> sports_ds core modules
```

Forbidden edges:

```text
generic skill guidance/scripts -X-> sports_ds
sports_ds core modules         -X-> sports_ds.pipelines
```

Tests enforce the first edge. Package structure and review enforce the second.

## Standalone skill contract

Every generic skill must:

- state the task it performs and when it applies;
- document the minimum input fields or artifact shape;
- work with a skill-only installation;
- use only public dependencies in bundled helpers;
- resolve helpers and references relative to its own `SKILL.md`;
- avoid repository-root paths, editable installs, toolkit CLI commands, and
  pipeline-specific schemas;
- validate required inputs before analysis;
- treat another skill as an optional handoff, never an undeclared runtime.

A skill does not need a script when judgment and code guidance are sufficient.
When a script exists, `--help` must work in isolation without network access or
the optional toolkit.

## Portable artifacts

Skills exchange ordinary files owned by the user's project:

- CSV or Parquet for observation, feature, prediction, and schedule tables;
- JSON for fold metrics, calibration summaries, simulations, and reports;
- Markdown for charters, audit notes, experiment logs, and model cards.

Each consumer owns and validates its exact schema. Producers must not rely on
filenames or implicit pipeline provenance to communicate meaning.

## Optional toolkit layout

```text
src/sports_ds/
  data/          # nfl/nba/mlb loaders and normalized panels
  eda/
  features/      # time-safe team and player features
  ratings/
  metrics/
  audit/
  models/
  validation/
  pipelines/     # optional reference orchestration
  cli.py
```

Core modules remain usable without importing `pipelines`. Pipelines compose
core modules and may expose compatibility aliases, but core ownership of schemas,
constants, metrics, and transformations must stay outside orchestration.

## Standard methodology

The following is a composable path, not a required pipeline:

```text
question -> data -> EDA -> legal features / ratings -> baselines
         -> model -> time-ordered validation -> trust checks
         -> interpretation / simulation / reporting
```

An agent loads only the skills relevant to the request.

## Verification

Repository checks should prove both products independently:

1. validate every skill's structure;
2. reject `sports_ds` imports outside `sports-ds-bridge`;
3. run every helper's `--help` from an unrelated working directory;
4. smoke-test representative helpers on synthetic portable artifacts;
5. run the optional toolkit's unit and integration suite;
6. retain optional live-data tests behind explicit environment gates.
