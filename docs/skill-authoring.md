# Skill authoring guide

Write focused, self-contained agent skills for sports analytics and modeling.

Use [../templates/skill/SKILL.md](../templates/skill/SKILL.md) as the starting
point.

## One skill, one job

Good boundaries:

- `leakage-audit` audits feature and evaluation leakage;
- `validation-design` designs honest validation;
- `statistical-modeling` selects and diagnoses statistical models.

Do not create a universal workflow skill or force every task through the same
pipeline.

## Frontmatter

```yaml
---
name: kebab-case-id
description: >
  State what the skill does and the requests that should activate it.
license: MIT
---
```

Only use fields supported by the current skill validator. Repository or skill
release versions belong in package metadata or `metadata`, not an unsupported
top-level key.

## Self-contained boundary

A user may install the skill without cloning this repository. Therefore a
generic skill must not:

- import or instruct the user to install `sports_ds`;
- invoke the `sports-ds` CLI or its pipelines;
- assume the current directory contains `skills/`, `src/`, or `pyproject.toml`;
- depend on a repository-level document;
- require another skill to complete its core job;
- assume an artifact came from a particular producer.

The sole exception is `sports-ds-bridge`, whose job is explicit optional
integration with the toolkit.

## Entrypoint content

Keep `SKILL.md` as short as the task permits. Include:

1. discriminating use and non-use boundaries;
2. required inputs, including grain and minimum fields;
3. the workflow and non-obvious sports-specific decisions;
4. hard constraints such as decision-time legality;
5. an observable output contract;
6. links to references and helpers only where relevant.

Move detailed schemas, mode-specific methods, and substantial examples into
`references/`. Do not duplicate the same guidance across files.

## Input and output artifacts

Generic computational helpers consume files owned by the user's project:

- CSV or Parquet for tabular data;
- JSON for metrics and structured results;
- Markdown for charters, logs, cards, and reports.

Document and validate required fields. Accept explicit column mappings when
common naming variants are reasonable. Do not infer validation design or
decision time from a filename.

## Scripts

Ship a script only when deterministic execution or repeated logic adds value.
Scripts must:

- use public dependencies only;
- accept user-owned input paths rather than loading a hidden canonical dataset;
- validate missing columns with actionable errors;
- parse `--help` before importing optional heavy packages;
- resolve sibling resources from `__file__`, never the process CWD;
- write only to explicit or clearly documented output paths;
- be tested on synthetic artifacts.

Reference a helper as:

```bash
python <path-to-this-skill>/scripts/helper.py --help
```

The agent resolves the actual installed skill path from the loaded `SKILL.md`.

## Public data skills

Source-specific skills may use the public package named by the skill, such as
`nflreadpy`, `sportsdataverse`, or `pybaseball`. They must disclose network,
cache, and package requirements and export portable files for downstream skills.

## Optional toolkit bridge

Generic skills may mention `sports-ds-bridge` only as an optional handoff when
the user asks for the toolkit or needs its supported data adapters. Do not place
toolkit commands or schemas in generic skills.

## Validation

```bash
python /path/to/skill-creator/scripts/quick_validate.py skills/<skill>
python skills/<skill>/scripts/<helper>.py --help
pytest -q
```

Also verify behavior on realistic synthetic input. Structural validation does
not prove that the skill makes good decisions.
