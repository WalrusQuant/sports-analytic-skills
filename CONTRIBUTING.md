# Contributing

Thanks for helping improve Sports Analytic Skills.

## What this project is

A standalone sports modeling **skill pack** for AI agents, plus an optional
`sports_ds` toolkit connected through `sports-ds-bridge`. Public docs should
help a stranger use the skills without discovering a hidden package dependency.

## Skill shape

Every skill lives under `skills/<id>/` and should include:

- `SKILL.md` — full operator manual
- `references/` — deep method detail
- `scripts/` — runnable helpers when useful

Use [templates/skill/SKILL.md](./templates/skill/SKILL.md) and [docs/skill-authoring.md](./docs/skill-authoring.md).

## Quality bar

A skill is in good shape when it has:

- a discovery-grade description in frontmatter
- clear when-to-use guidance
- an ordered workflow
- sports-specific decision tables / code
- worked examples on public data
- hard constraints (time safety, baselines, honest metrics)
- scripts documented in the skill when shipped
- explicit input/output contracts
- no `sports_ds`, CLI, pipeline, or repository-root dependency outside the bridge

## Scope

In scope:

- sports data loading, EDA, features, ratings, stats/ML, validation, simulation, reporting
- multi-sport methodology
- public data ecosystems (nflverse, SportsDataverse, pybaseball, …)

Out of scope for this pack:

- pick selling / tip services
- guaranteed-profit framing
- book account automation

## Docs

- Keep the README a real product page (why, getting started, examples, catalog, layout)
- No private tracker IDs or personal runtime notes in public docs
- Prefer clear explanation over inventory-only dumps

## Scripts and tests

If you add scripts:

- keep them small and readable
- accept user-owned artifacts and public dependencies
- make `--help` work from an unrelated directory
- validate required columns and formats
- add or update standalone behavioral tests
- document how to run them in `SKILL.md`

## Review checklist

- [ ] Does this help an agent run a real sports analysis path?
- [ ] Is time safety respected for predictive work?
- [ ] Are baselines and validation honest?
- [ ] Can a stranger follow the docs without chat history?
- [ ] Does the skill still work when installed without this repository?
