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

## Entrypoint content and instructional depth

Keep `SKILL.md` focused, but never shorten it by deleting guidance that changes
an agent's decisions. Portability and instructional depth are independent
requirements. A deep skill may distribute material across `SKILL.md` and
`references/`; the installed skill as a whole must remain a usable operator
manual.

Include or explicitly route all of the following when they are part of the job:

1. discriminating use and non-use boundaries;
2. required inputs, grain, timing, keys, and minimum fields;
3. the end-to-end workflow and non-obvious sports-specific decisions;
4. decision tables for choosing methods, metrics, or modes;
5. diagnostics, failure modes, anti-patterns, and remediation;
6. a worked path that shows how the parts fit together;
7. interpretation and reporting requirements;
8. hard constraints such as decision-time legality;
9. an observable output contract;
10. bundled references and helpers, with precise routing instructions.

Use progressive disclosure for genuinely conditional detail. Move a substantial
example, schema, or mode-specific procedure only after creating the destination
reference, and link it from the point where the agent needs it with wording such
as “read this before fitting a count model.” A bare `references/` directory is
not a substitute for routing. Do not duplicate the same guidance across files.

### Migration preservation review

For any broad rewrite or portability migration:

1. inventory the existing headings, decision tables, examples, diagnostics,
   templates, integrity rules, references, and helper contracts;
2. classify each removal as obsolete, package-coupled, duplicated, or still
   generally useful;
3. preserve generally useful material in place or move it to an explicitly
   routed reference;
4. compare the before/after instructional inventory and investigate every large
   unexplained deletion;
5. test execution and portability separately from content completeness.

Passing a validator or smoke test does not prove that the skill retained its
methodology. A migration with unexplained wholesale documentation deletion fails
review even when all executable tests pass.

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
not prove that the skill makes good decisions. Review reference routing and the
migration preservation inventory whenever documentation changes materially.
