# Skill Independence Audit

## Why

The repository should primarily provide reusable sports-analysis and modeling skills. The bundled `sports_ds` package and end-to-end pipelines may be useful examples, but individual skills must remain usable without adopting or running that pipeline.

## Shape of done

- Every skill has a documented purpose, inputs, outputs, dependencies, and standalone invocation path.
- Installing only the skills is sufficient; generic skills do not require `sports_ds`.
- Pipeline-specific imports, file layouts, schemas, and CLI assumptions are identified.
- A representative standalone smoke test proves skill scripts work outside the repository pipeline.
- Any required decoupling changes are minimal, reviewed, and covered by tests.

## Audit and plan

- [x] Inventory skills, helper scripts, package code, tests, and documented workflows.
- [x] Map direct and indirect dependencies from each skill to `sports_ds`, pipeline modules, repository-relative paths, and shared schemas.
- [x] Run the existing test suite and representative skill scripts to establish a baseline.
- [x] Classify each skill as standalone, standalone-with-optional-library, or pipeline-coupled.
- [x] Write audit findings and a minimal decoupling design.
- [x] Check in before implementation changes. User confirmed the strict skill-only boundary.

## Implementation

- [x] Define the standalone artifact contracts shared by analysis/modeling skills.
- [x] Make every generic skill and helper usable without importing `sports_ds` or assuming the repository root.
- [x] Add one dedicated `sports_ds` bridge skill for optional data acquisition, core helpers, CLI, and pipelines.
- [x] Remove generic-skill documentation that prescribes `pip install -e .`, `sports-ds`, or repository-relative sibling commands.
- [x] Fix invalid skill frontmatter and broken helper imports discovered by the audit.
- [x] Reframe the README, architecture, charter, getting started guide, runbook, roadmap, plugin metadata, and authoring standard around skill-only installation.
- [x] Add validation, forbidden-import, isolated `--help`, and representative toy-data smoke tests.
- [x] Run focused and full verification.
- [x] Review the diff for correctness, simplicity, and refactoring opportunities.

## Review

### Baseline

- `pytest -q`: 29 passed, 6 skipped, 84 warnings.
- Plain Python cannot import `sports_ds` in the current checkout; pytest succeeds because `pyproject.toml` injects `src` only for tests.
- 38 skill scripts exist; 23 import `sports_ds`; 11 import `sports_ds.pipelines`.
- 10 of those 11 pipeline imports only retrieve `FEATURE_COLS`. The lists are identical to the existing core constant `DEFAULT_WIN_FEATURE_COLS`.
- Direct isolated `--help` checks fail for 19 of 32 argparse scripts. With `PYTHONPATH=src`, 29 pass and 3 fail.
- No existing test invokes a skill script.
- All 23 skills fail the current Codex skill validator because their frontmatter contains unsupported top-level `version`.

### Classification

- Standalone (7): anti-slop-analytics, data-sources, experiment-log, model-card, pybaseball, simulation-sports, sports-modeling-doctrine.
- Optional reusable-library dependency (6): eda-sports, nflreadpy, sportsdataverse-py, statistical-modeling, time-series-sports, validation-design.
- Pipeline-coupled in code, artifact schema, or required workflow (10): baseline-models, calibration-check, environment-setup, feature-rules, leakage-audit, model-interpretation, predictive-modeling, ratings-strength-models, results-reporting, sports-visualization.

### Findings

1. The core package already has the right dependency direction: reusable `audit`, `data`, `eda`, `features`, `metrics`, `models`, `ratings`, and `validation` modules do not import pipelines.
2. The main code leak is concentrated: ten skill scripts import pipeline-owned copies of a feature list that already has a core owner; one Elo script genuinely calls a pipeline.
3. The larger portability leak is repository context: all skill manuals use `python skills/...`, most prescribe `pip install -e .`, and several depend on repository-level docs. An agent-host skill install therefore does not provide the runtime implied by the manuals.
4. Many helpers load canonical NFL/NBA/MLB panels internally and provide no `--input` path for user-owned CSV/Parquet data.
5. Reporting, visualization, and simulation consume implicit artifact schemas without complete validation; reporting can claim walk-forward validation regardless of artifact provenance.
6. The green package suite does not prove standalone skill behavior.
7. Separate runtime defects: `segment_calibration.py` imports nonexistent `log_loss`; the allowed local combination of statsmodels 0.14.1 and SciPy 1.16.3 breaks two statistical helpers during import.

### Confirmed boundary

```text
generic skill guidance/scripts ──> user artifacts + public dependencies
sports-ds bridge skill          ──> optional sports_ds package/CLI/pipelines
sports_ds pipelines             ──> sports_ds core APIs

generic skill guidance/scripts -X-> sports_ds (including pipelines)
sports_ds core                  -X-> sports_ds.pipelines
```

Pipelines remain optional examples and CLI accelerators behind the bridge skill. A user who installs only the generic skills must not be sent to a missing package.

### Implemented result

- Converted all 23 original skills to portable user-artifact interfaces and added the dedicated `sports-ds-bridge` skill.
- Removed generic-skill imports, install instructions, CLI calls, and working-directory assumptions tied to `sports_ds`.
- Added explicit standalone panel, fold-metric, held-out-prediction, calibration, Elo, simulation, visualization, and reporting handoffs.
- Fixed audit defects in leakage verdicts, time ordering, feature legality, empty-input handling, NFL panel construction, Elo probabilities, calibration filtering, EDA reporting, templates, and headless plotting.
- Updated project and authoring documentation so skill-only installation is the primary product and `sports_ds` is optional.

### Final verification

- `pytest -q`: 44 passed, 7 skipped, 84 pre-existing warnings.
- Standalone skill smoke suite: user CSV → model fold JSON + held-out predictions → calibration + visualization passed outside the repository working directory.
- All 24 skills pass the current `quick_validate.py` validator.
- Every Python helper compiles and exposes isolated `--help`; boundary tests reject generic `sports_ds`, editable-install, and repository-relative command dependencies.
- `git diff --check` passes.
- Code review findings were corrected before the user-requested commit.

## Local toolkit environment

- [x] Confirm `.venv/` is ignored by Git.
- [x] Create the repository-local virtual environment.
- [x] Install the `dev` and `multi` dependency groups.
- [x] Run the offline test suite with skip reasons.
- [x] Run explicitly gated live-data tests and record upstream failures separately.

### Environment verification

- Created ignored `.venv/` with Python 3.12 and installed `.[dev,multi]`.
- Installed Homebrew `libomp` for the XGBoost runtime required by `sportsdataverse`.
- Homebrew cleanup removed `ripgrep` incidentally; restored it immediately at version 15.2.0.
- Sandboxed suite: 45 passed, 7 network/live-gated skips, 75 warnings.
- Fully enabled live suite: 52 passed, 0 skipped, 115 performance warnings.

## Player-form performance warning cleanup

- [x] Trace all 115 live-suite warnings to repeated derived-column insertion in `player_form.py`.
- [x] Batch numeric normalization and derived-feature assembly without changing feature semantics.
- [x] Add warning-as-error regression coverage and value/order invariants.
- [x] Run focused MLB player tests and the full offline/live suites.
- [x] Review the refactor for output parity, simplicity, and unintended changes.

### Warning cleanup result

- Replaced repeated feature-column insertion with two order-preserving batched merges: one for normalized source statistics and one for all derived features.
- Direct comparison with the pre-change implementation matched a representative 288-row × 150-column artifact exactly, including values, dtypes, index, and column order.
- Focused NFL/NBA/MLB player-form tests pass with pandas `PerformanceWarning` promoted to an error.
- Fully enabled live suite passes with `52 passed`, `0 skipped`, and no warnings.
- `git diff --check` passes; included in the user-requested commit.
