# Contributing

This project is currently private craft work. This file still defines the contribution bar so the repo stays public-library quality from day one.

## Current mode

- Design and documentation first
- Skills are drafted in `skills/` only when ready to be real
- Do not install into OpenClaw or other runtimes from this repo unless explicitly requested
- Do not create Skill Workshop proposals unless explicitly requested

## What good looks like

### Docs changes

- Keep planned vs shipped honest
- Update README badges/counts if skill inventory changes
- Cross-link architecture, taxonomy, and roadmap when structure changes
- No emoji-required style; plain clear writing wins

### New skills

1. Open from [templates/skill/SKILL.md](./templates/skill/SKILL.md)
2. Follow [docs/skill-authoring.md](./docs/skill-authoring.md)
3. Meet [docs/documentation-standard.md](./docs/documentation-standard.md)
4. Add the skill to taxonomy/roadmap only when the draft is real
5. Prefer one sharp skill over three vague ones

### Skill quality gate

A skill may be considered mergeable when:

- discovery-grade frontmatter description exists
- when/when-not gates are explicit
- hard constraints and anti-patterns are real
- output contract is checkable
- worked example exists (synthetic/public default)
- no tip-service or autobet behavior
- no single-sport bias unless it is a declared sport module

### Scripts

If a skill ships `scripts/`:

- keep them small and readable
- include `tests/`
- document inputs/outputs in `SKILL.md`
- no hidden network side effects by default

## Scope boundaries

In scope:

- multi-sport modeling methodology
- validation, leakage, critique
- market evaluation layered onto modeling
- later sport modules as domain constraints

Out of scope:

- pick selling
- guaranteed profit systems
- book account automation
- private bankroll productization

## Review checklist

- [ ] Does this reduce agent slop in sports analytics?
- [ ] Is it sport-agnostic unless intentionally a sport module?
- [ ] Are claims honest?
- [ ] Are docs complete enough for a stranger?
- [ ] Did we avoid fake “complete library” language?
