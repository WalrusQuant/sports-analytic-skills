# Contributing

Thanks for helping improve Sports Analytic Skills.

## What this project is

A markdown skill pack for sports modeling. Data comes from sportsleader-data, through the public Parquet manifest or the sports-leader connector. This repository does not contain a Python package, tests, or bundled programs.

## Skill shape

Every skill lives under `skills/<id>/`:

- `SKILL.md` with `name` equal to the folder, a discovery description, `license: MIT`, and `metadata.version`
- `references/` for detail that should load only when needed

Start from [templates/skill/SKILL.md](./templates/skill/SKILL.md) and [docs/skill-authoring.md](./docs/skill-authoring.md).

## Quality bar

- The description says what the skill does and when to load it.
- The workflow is ordered and the inputs are explicit.
- Predictive work states decision time, a baseline, and a time-ordered check.
- Examples may show a short pandas or DuckDB read of a Parquet file. They must not depend on a path inside this repository.
- Dataset names and columns match the sportsleader-data manifest. Do not invent them.
- Relative links in markdown resolve.

## Scope

In scope: EDA, features, ratings, statistical and predictive models, validation, simulation, and reporting for the six leagues sportsleader-data publishes.

Out of scope: pick selling, guaranteed-profit framing, and betting-execution workflows. The pack is a research tool.

## Docs

Keep the README a product page. The GitHub Pages site is `docs/index.html` and `docs/docs.html`. Do not put private tracker ids or secrets in public docs.

## Review

- [ ] Does this help an agent run a real sports analysis?
- [ ] Is time safety respected for predictive work?
- [ ] Are baselines and validation honest?
- [ ] Can a stranger follow the docs without chat history?
- [ ] Does the skill still make sense when installed without this repository?
