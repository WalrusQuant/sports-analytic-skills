# Documentation standard

Public docs help a stranger use the standalone sports modeling skills. The
optional toolkit is a secondary integration path.

## Public front door (README)

The README is a **product page**, not a project tracker.

It should include:

1. What the library is
2. Skill-only install + first prompts
3. Skill inventory with jobs and artifact expectations
4. Optional bridge/toolkit overview
5. Design rules
6. Links to deeper docs
7. License

It should **not** include:

- personal status diaries
- private tracker IDs
- “done / next / blocked” project management tables
- chat-process language

## Deep docs

| Doc | Job |
|---|---|
| `README.md` | Public orientation |
| `ARCHITECTURE.md` | System design |
| `CONTRIBUTING.md` | Contribution and quality gates |
| `docs/getting-started.md` | Install/use |
| `docs/skill-authoring.md` | How to write deep skills |
| `docs/taxonomy.md` | Domains and skill IDs |
| `docs/data-ecosystem.md` | Public sports data sources |
| `docs/environment.md` | Runtime deps |
| `docs/roadmap.md` | Sequencing for depth expansion |

## Writing style

- Direct, technical
- Sports modeling language
- Prefer decision tables and code over slogans
- Short sections
- Write for strangers and agents

## Skill doc minimum

See `docs/skill-authoring.md`. Each installed skill must preserve the complete
decision-changing operator guidance for its job, whether that guidance lives in
`SKILL.md` or explicitly routed references. Length alone does not prove quality,
but a large unexplained deletion is a review failure, not an optimization.
