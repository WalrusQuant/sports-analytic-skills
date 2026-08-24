# Skill authoring guide

How to write skills for this repo.

Template: [../templates/skill/SKILL.md](../templates/skill/SKILL.md)

## One skill = one job

Good:

- `leakage-audit` audits leakage
- `validation-design` designs validation
- `clv-evaluation` evaluates closing-line performance

Bad:

- `sports-analytics-everything`
- `nfl-and-also-bankroll-and-also-scrapers`

If you need two jobs, write two skills and hand off.

## Frontmatter rules

```yaml
---
name: kebab-case-id
description: >
  What it does and when to load it.
  Include trigger phrases an agent can match.
version: "0.x.y"
license: MIT
---
```

Description quality bar:

- specific enough for discovery
- includes when-to-use signals
- not marketing copy
- no fake breadth

## Required sections

### When to use

Concrete triggers.

### When not to use

Explicit refusals / better handoffs.

### Required inputs

Data, metadata, constraints. Mark optional clearly.

### Procedure

Numbered steps an agent can execute without inventing forbidden shortcuts.

### Hard constraints

Non-negotiables. These are the hard rules the agent must not bend.

Examples:

- no future-knowing features
- no “guaranteed edge” claims
- if no market data, mark paper-only

### Anti-patterns

Top real failure modes, not filler.

### Output contract

Checklist of what “done” means. Must be checkable.

### Handoffs

Which skills come next, and when to stop.

### Worked example

Synthetic or public data default. Keep it short and real.

### References

Methods, papers, standards, prior art.

## Foundation triad boundaries

Do not dump everything into `doctrine`.

| Skill | Owns | Does not own |
|---|---|---|
| `doctrine` | edge definition, evidence rank, ship/kill | legal/claim refusals, stake math language |
| `ethics` | honesty, refusals, not-advice, anti-hype | validation mechanics |
| `risk` | uncertainty, calibration framing, stake discipline language | full bankroll product design |

If a sentence fits two, put it in the narrower skill.

## Modeling-first rule

Core skills should work without a sportsbook.

Market concepts enter when:

- evaluating claims against markets
- cleaning odds panels
- deciding whether a model may claim actionable edge

A modeling skill may hand off to market skills. It should not hard-require them for basic validity work.

## Sport modules

Only after core is stable.

A sport module must add constraints the core cannot express, for example:

- clock/possession structure
- scoring process quirks
- substitution/lineup constraints
- season/playoff regime rules

Not allowed as a sport module:

- wiki recap of the sport
- favorite-team lore
- generic ML restated with league nouns

No sport is the default first module.

## Scripts policy

Scripts are optional helpers.

Ship scripts only when they:

- encode a deterministic check worth reusing
- are small enough to audit
- have tests
- are documented in the skill

Judgment stays in markdown.

## Naming

- IDs: `kebab-case`
- prefer durable methodology names over brand names
- avoid bookmaker-specific skill names in core

## Draft vs ready

| State | Meaning |
|---|---|
| planned | listed in taxonomy/roadmap only |
| draft | exists under `skills/` but incomplete |
| ready | passes quality gate in CONTRIBUTING.md |

README counts only ready/draft with honest labels. Do not market planned skills as included.
