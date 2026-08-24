# Skill authoring guide

How to write skills for this repo.

Quality bar: deep scientific-style agent skills, specialized for **sports modeling and analytics**.

Template: [../templates/skill/SKILL.md](../templates/skill/SKILL.md)

## One skill = one job

Good:

- `leakage-audit` audits leakage
- `validation-design` designs validation
- `statistical-modeling` runs sports GLMs and diagnostics

Bad:

- `sports-analytics-everything`
- skills that only restate the README

If you need two jobs, write two skills and hand off.

## Frontmatter

```yaml
---
name: kebab-case-id
description: >
  What it does and when to load it.
  Include trigger phrases an agent can match.
  Be specific and long enough for discovery.
version: "0.x.y"
license: MIT
---
```

## Required depth

Every skill should include:

1. **Overview** — what the agent will produce
2. **When to use** — concrete triggers
3. **Installation** — packages / `sports_ds` if needed
4. **Workflow** — ordered steps
5. **Sports decision tables** — model/test/metric choices for sports outcomes
6. **Code** — `sports_ds` APIs, CLI, or loader examples
7. **Scripts** — `scripts/*.py` agents can run
8. **References** — `references/*.md` for method detail
9. **Worked example** — public sports data
10. **Reporting template** — what a finished answer looks like
11. **Hard constraints** — non-negotiables (time safety, baselines, etc.)

## Scripts policy

Ship scripts when they:

- encode a reusable sports analysis check
- run against public data or `sports_ds`
- are small enough to audit
- are documented in the skill

Judgment stays in markdown. Execution helpers live in scripts.

## Naming

- IDs: `kebab-case`
- prefer durable methodology names
- sports-specific where the method is sports-specific

## Modeling-first rule

Core skills work on sports outcomes and public sports data.
They do not require sportsbook/odds workflows to be useful.
