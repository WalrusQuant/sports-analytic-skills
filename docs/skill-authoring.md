# Skill authoring guide

Write a self-contained agent skill for one sports-analytics job.

Use [../templates/skill/SKILL.md](../templates/skill/SKILL.md) as the starting point.

## One skill, one job

Good boundaries:

- `leakage-audit` audits feature and evaluation leakage;
- `validation-design` designs honest validation;
- `data-sources` chooses a sportsleader-data file.

Do not create a universal workflow skill.

## Frontmatter

```yaml
---
name: kebab-case-id
description: >
  State what the skill does and the requests that should activate it.
license: MIT
metadata:
  version: "1.0.0"
---
```

`name` matches the directory under `skills/`. Keep `license: MIT`. Bump `metadata.version` when the skill's contract changes. The pack version is also `plugin.json`.

## Boundary

A user may install the skill without cloning this repository. A skill must not:

- tell the user to install a package from this repository;
- assume the working directory contains this repo;
- depend on a program stored next to `SKILL.md`;
- invent a sportsleader-data dataset or column.

Illustrative snippets may use pandas or DuckDB on a public Parquet URL or on a file the user owns.

## What to include

1. When to use the skill, and when not to.
2. Inputs, grain, timing, keys, and minimum fields.
3. The workflow and the sports-specific decisions.
4. Failure modes and anti-patterns.
5. A worked path.
6. An output contract.
7. Links to `references/` for conditional detail.

Data acquisition goes through `data-sources`. Do not add a second acquisition skill for a single league.

## Artifacts

Skills talk about files the user owns:

- Parquet or CSV for tables;
- JSON for metrics;
- Markdown for charters, logs, cards, and reports.

Copy sportsleader-data column names from the manifest entry for that file.

## Review

Read the skill as a cold agent. Check that every relative link resolves, the frontmatter parses, and the text does not name a program in this repository.
