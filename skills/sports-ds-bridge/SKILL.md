---
name: sports-ds-bridge
description: >
  Connect the optional sports_ds Python toolkit to the standalone sports
  analytics skills. Use when the user explicitly mentions sports_ds, wants its
  NFL/NBA/MLB public-data loaders or CLI, needs toolkit setup/troubleshooting,
  or wants to convert toolkit output into a skill's documented input artifact.
---

# Sports DS Bridge

`sports_ds` is an optional data and workflow accelerator. It is not required by
the other skills. Use this bridge to acquire or normalize data, materialize a
portable artifact, and then hand that artifact to the relevant standalone skill.

## Do not use this bridge

- For ordinary EDA, modeling, validation, or reporting when the user already
  has usable data.
- To replace the user's existing data stack or modeling code.
- To make a generic skill depend on this repository or its pipeline outputs.

## Workflow

1. Identify the downstream skill and its required columns or JSON fields.
2. Check whether `sports_ds` is already importable before suggesting setup.
3. If it is missing, explain that it is optional. Install or clone it only with
   the user's authorization.
4. Prefer reusable loader/core APIs when the task needs data or one transform.
   Use a pipeline command only when the user explicitly wants an end-to-end
   reference workflow.
5. Write a portable CSV, Parquet, or JSON artifact in the user's project.
6. Validate the artifact against the downstream skill's own input contract.
7. Continue with the standalone skill; do not make it call back into
   `sports_ds`.

## Setup checks

```bash
python -c "import sports_ds; print(sports_ds.__version__)"
sports-ds --help
```

When the toolkit is not installed, the source repository is
`https://github.com/WalrusQuant/sports-analytic-skills`. Keep environment
changes scoped to the user's project and get approval before installing.

## Choose the narrowest toolkit surface

| Need | Prefer | Avoid unless requested |
|---|---|---|
| NFL schedules or team-game data | `sports_ds.data.nfl` | full win pipeline |
| NBA/MLB team-game data | `sports_ds.data.nba` / `.mlb` | unrelated model pipeline |
| Player-game data | matching `sports_ds.data.*_players` loader | team pipeline |
| Time-safe features | `sports_ds.features` | copying pipeline internals |
| Elo ratings | `sports_ds.ratings` | end-to-end CLI run |
| Metrics, splits, leakage checks | matching core module | pipeline-owned constants |
| Reproducible reference benchmark | `sports-ds` CLI pipeline | treating its artifact as universal |

Read [references/toolkit-map.md](references/toolkit-map.md) for concrete imports
and CLI routes. Read [references/handoff-contracts.md](references/handoff-contracts.md)
when materializing an artifact for another skill.

## Hard constraints

- Never imply that `sports_ds` is installed merely because this skill exists.
- Never tell a generic skill to import `sports_ds`.
- Never present pipeline-specific field names as a universal schema.
- Do not install packages, download large datasets, or overwrite artifacts
  without the user's authorization.
- Preserve decision-time integrity when exporting pre-game features: every
  value must be knowable at or before the declared prediction time.

## Output contract

Finish with:

- the toolkit surface used and why;
- the artifact path and format;
- its grain, time window, and required-column validation;
- the standalone skill that can consume it;
- any optional dependencies, cache behavior, or provenance limitations.
