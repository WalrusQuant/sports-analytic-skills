# Documentation standard

We are matching the **documentation seriousness** of high-quality public skill libraries (especially K-Dense), not their inventory size.

## Why this file exists

A skill pack fails quietly when:

- the README is thin
- planned work is written as if shipped
- install story is missing
- skill contracts are inconsistent
- strangers cannot tell what the system is for

Documentation is part of the product.

## Public front door (README) must include

1. One-sentence identity
2. Honest status table (planned vs shipped)
3. Why it exists / problem statement
4. What it is / what it is not
5. Design principles
6. Architecture overview with pointer to deep doc
7. Inventory section (real counts only)
8. Planned map clearly labeled planned
9. Repo layout
10. Getting started (even if “not installable yet”)
11. Skill structure contract
12. Security/trust notes
13. Disclaimer
14. Roadmap pointer
15. Contributing pointer
16. FAQ
17. Prior art
18. License + citation

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
- Use “planned”, “draft”, “shipped” language explicitly
- Examples must be synthetic or public unless user-supplied private data is clearly marked
- Do not imply runtime install when none exists
- Do not imply multi-agent harness until it exists

## Writing style

- Direct, technical, low hype
- No tip-shop language
- No single-sport favoritism in core docs
- Prefer tables and contracts over vibes
- Short sections with anchors over walls of lore

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

## Definition of “docs are good enough to publish”

- stranger understands the project in 3 minutes from README
- stranger can find architecture and authoring rules without chat history
- no section claims capabilities that are not in the repo
- install path is either real or clearly marked planned
- at least one complete example skill exists before public launch

## K-Dense lessons we are copying

- deep README with TOC and explicit sections
- clear compatibility/standard badges
- install story for multiple hosts
- security/trust framing
- FAQ and contribution path
- skill packaging consistency
- separation of “what’s included” from marketing fluff

## K-Dense lessons we are not copying yet

- 100+ skill inventory on day one
- commercial support positioning
- webinar/product funnel language
- emoji-heavy presentation
