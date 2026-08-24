# Documentation standard

Documentation is part of the product. Public docs should help a stranger understand and use the library without private context.

## Why this file exists

A skill pack fails quietly when:

- the README is thin
- planned work is written as if shipped
- install story is missing
- skill contracts are inconsistent
- strangers cannot tell what the system is for
- public docs mix in private trackers or internal process notes

## Public vs internal

Public docs (README, architecture, skill files, getting started, contributing):

- no private project-tracker IDs
- no personal runtime install state
- no internal chat/process diary language
- prior art belongs in a short dedicated section, not constant comparisons

Internal notes, if needed, stay out of the public front door.

## Public front door (README) must include

1. One-sentence identity
2. Honest status table (planned vs drafted vs ready)
3. Why it exists / problem statement
4. What it is / what it is not
5. Design principles
6. Architecture overview with pointer to deep doc
7. Inventory / available skills section
8. Repo layout
9. Getting started
10. Skill structure contract
11. Security/trust notes
12. Disclaimer
13. Roadmap pointer
14. Contributing pointer
15. FAQ
16. Prior art
17. License + citation

## Deep docs map

| Doc | Job |
|---|---|
| `README.md` | Public orientation |
| `ARCHITECTURE.md` | System design truth |
| `CONTRIBUTING.md` | Contribution and quality gates |
| `docs/roadmap.md` | Sequencing |
| `docs/taxonomy.md` | Skill domains and IDs |
| `docs/getting-started.md` | Install/use paths |
| `docs/skill-authoring.md` | How to write skills |
| `docs/documentation-standard.md` | This file |
| `references/prior-art.md` | Lineage and standards |

## Honesty rules

- Never badge a skill count higher than drafted skills
- Use “planned”, “draft”, “ready” language explicitly
- Examples must be synthetic or public unless user-supplied private data is clearly marked
- Do not imply a polished product release when drafts are early
- Do not imply multi-agent harness until it exists

## Writing style

- Direct, technical, low hype
- No tip-shop language
- No single-sport favoritism in core docs
- Prefer tables and contracts over vibes
- Short sections with anchors over walls of lore
- Write for strangers, not for the authors’ private workflow

## Skill doc minimum

Every `SKILL.md` needs:

- discovery description
- when / when not
- inputs
- procedure
- hard constraints
- anti-patterns
- output contract
- handoffs
- worked example
- references

## Definition of “docs are good enough”

- stranger understands the project in 3 minutes from README
- stranger can find architecture and authoring rules without chat history
- no section claims capabilities that are not in the repo
- install path is clear
- public pages do not leak private tracking or machine-specific state
