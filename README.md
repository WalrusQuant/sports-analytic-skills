# Sports Analytic Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.0.1-blue.svg)](plugin.json)
[![Skills](https://img.shields.io/badge/Skills-0_drafted-lightgrey.svg)](#planned-skill-map)
[![Status](https://img.shields.io/badge/Status-design_scaffold-orange.svg)](#project-status)
[![Standard](https://img.shields.io/badge/Standard-Agent_Skills-blueviolet.svg)](https://agentskills.io/)
[![Plugins](https://img.shields.io/badge/Standard-Agent_Plugins-0A7A72.svg)](https://agent-plugins.org/)
[![Works with](https://img.shields.io/badge/Target-Cursor_|_Claude_Code_|_Codex_|_OpenClaw-blue.svg)](#getting-started-planned)

> Multi-sport data science judgment for AI agents.  
> Portable `SKILL.md` packages that teach an agent how a sharp analyst models sports — and how to refuse bad work.

**Sports Analytic Skills** is an open, free Agent Skills library for **sports modeling and sports analytics across sports**. It is built on the same open standards as [K-Dense Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills) and judgment-style packs like [Taste](https://github.com/leonxlnx/taste-skill):

- [Agent Skills](https://agentskills.io/) (`SKILL.md` + frontmatter discovery)
- [Agent Plugins](https://agent-plugins.org/) (`plugin.json` + `skills/`)

The goal is not another prompt dump. The goal is a **documented, installable methodology pack** any compatible agent host can load: Claude Code, Codex, Cursor, OpenClaw, and others.

**Cadence (private tracking):** Sports Analytic Skills (`3bdd6b88-4548-49f0-a0c1-f529695920d4`)

---

## Project status

| Item | State |
|---|---|
| Architecture | Locked (v0) |
| Public docs shape | In progress (this README + supporting docs) |
| Skills drafted | **0** (by design — docs/architecture first) |
| Published GitHub repo | Yes — https://github.com/WalrusQuant/sports-analytic-skills |
| Installable package | Not yet |
| Installed on this OpenClaw instance | **No** (intentional) |
| Skill Workshop / live apply | **No** (intentional) |

This repository is being built as a **real global project**, not a private one-off skill. Documentation quality is a first-class deliverable, not an afterthought.

---

## Table of contents

- [Why this exists](#why-this-exists)
- [What this is](#what-this-is)
- [What this is not](#what-this-is-not)
- [Design principles](#design-principles)
- [Architecture overview](#architecture-overview)
- [What's included (repo)](#whats-included-repo)
- [Planned skill map](#planned-skill-map)
- [Repository layout](#repository-layout)
- [Getting started (planned)](#getting-started-planned)
- [How a skill is structured](#how-a-skill-is-structured)
- [Documentation standard](#documentation-standard)
- [Security and trust](#security-and-trust)
- [Disclaimer](#disclaimer)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [FAQ](#faq)
- [Prior art](#prior-art)
- [License](#license)
- [Citation](#citation)

---

## Why this exists

General-purpose coding agents are fluent and sloppy at sports analytics.

They will:

- leak future information into features
- treat a pretty backtest as proof
- confuse model fit with market edge
- skip calibration and closing-line checks
- invent “systems” with no kill criteria
- write confident nonsense on NFL Monday the same way they do on random CSVs

Package docs alone do not fix that. Agents can already call pandas, scikit-learn, and statsmodels. What they lack is **portable judgment**: when a method is valid, what evidence ranks higher, and when to stop.

Taste fixed generic UI slop with design constraints.  
K-Dense fixed scientific workflow amnesia with a deep skill library and serious documentation.

This project is the sports-modeling version of that idea:

> Encode sharp multi-sport analytic discipline as installable skills.

---

## What this is

A **global open-source skill library** for:

- multi-sport predictive modeling
- validation and leakage control
- honest backtest critique
- probability quality / calibration framing
- sports market evaluation where it belongs (odds hygiene, CLV, claim limits)
- later: sport-specific modules (NFL, MLB, NBA, NHL, soccer, golf, and others)

### Core idea

| Layer | Role |
|---|---|
| Foundation triad | `doctrine` + `ethics` + `risk` |
| Modeling engine | baselines, features, leakage, validation, critique |
| Market layer | layered in at data + evaluation joints |
| Sport modules | later expansions only; none privileged |
| Harness | optional later (plan → run → critique) |

### Locked design choices

1. **Name:** `sports-analytic-skills`
2. **Foundation split:** separate `doctrine`, `ethics`, and `risk` skills
3. **Sport scope:** sport-agnostic multi-sport core; sport modules later (NFL, MLB, NBA, NHL, soccer, golf, etc.) with no favorite child
4. **Center of gravity:** modeling is the engine; market dynamics layer in where they fit best

---

## What this is not

- Not a betting tip service
- Not “locks of the day”
- Not a paid product or SaaS
- Not bankroll software
- Not an autobet / book-account bot pack
- Not a 100-empty-stub museum
- Not a single-sport hobby repo
- Not installed into a personal OpenClaw runtime during design

If a skill would mainly help someone spam picks, it does not belong here.

---

## Design principles

1. **Judgment over cookbook.** Skills teach refusal and standards, not only code snippets.
2. **Small and sharp beats huge and shallow.** A skill earns its folder.
3. **Sport-agnostic core.** The same spine works across sports; modules add constraints the core cannot express.
4. **Modeling first.** Baselines, features, leakage, validation, and critique are the spine.
5. **Markets as scoreboard, not identity.** CLV and odds hygiene matter; they do not turn every skill into betting content.
6. **Honest claims only.** No guaranteed +EV language. Paper-only when market proof is missing.
7. **Documentation is product.** README, architecture, skill contract, examples, and anti-patterns are required quality bars.
8. **Host-portable.** Skills target the open Agent Skills standard, not one vendor runtime.
9. **Free and open.** MIT. No product path.
10. **Separate library from install.** Publishing a skill pack is different from enabling it on any one machine.

---

## Architecture overview

Full detail: [ARCHITECTURE.md](./ARCHITECTURE.md)

```text
L3  Harness (optional, later)
    plan → execute → critique → kill/ship

L2  Workflow skills
    modeling spine + market layer + ops/comms

L1  Foundation triad
    doctrine | ethics | risk

Host runtime
    Claude Code / Codex / Cursor / OpenClaw / ...
    + user tools, data, MCP (outside this repo)
```

### Center of gravity

```text
modeling engine (core)
  baselines → features → validation → leakage → backtest critique
       │
       └── market layer (where it earns a slot)
             odds hygiene → vig → CLV / market eval → claim limits
```

Skills are **procedure + judgment**. They are not the data plane. Agents use whatever tools exist locally (code execution, databases, APIs, MCP servers). This repo binds methodology.

---

## What's included (repo)

Even before skills are drafted, the repository is structured like a real public pack:

| Piece | Purpose |
|---|---|
| [README.md](./README.md) | Public front door (this file) |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design source of truth |
| [plugin.json](./plugin.json) | Agent Plugins manifest |
| [LICENSE](./LICENSE) | MIT + research/not-advice disclaimer |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | How skills and docs get added |
| [docs/](./docs/) | Roadmap, taxonomy, authoring, getting started |
| [templates/skill/](./templates/skill/) | Canonical `SKILL.md` template |
| [references/](./references/) | Prior art and external standards |
| `skills/` | One folder per skill (empty until drafted) |

Each future skill is expected to include:

- comprehensive `SKILL.md` documentation
- when-to-use / when-not-to-use gates
- hard constraints and anti-patterns
- checkable output contract
- handoffs to related skills
- at least one worked example (synthetic or public data by default)
- optional `scripts/`, `references/`, `assets/`, `tests/` when earned

---

## Planned skill map

Nothing below is shipped yet. This is the architecture map, not a fake feature list.

### Foundation (L1)

| Skill ID | Job |
|---|---|
| `doctrine` | Edge vs noise, evidence hierarchy, ship / paper-only / kill |
| `ethics` | Honesty bounds, refusals, anti-snake-oil, not-advice posture |
| `risk` | Uncertainty, calibration language, stake discipline framing |

### Modeling spine

| Skill ID | Job |
|---|---|
| `baseline-models` | Strong baselines before complexity |
| `feature-rules` | Time-safe, leakage-aware feature design |
| `leakage-audit` | Look-ahead and target leakage review |
| `validation-design` | Walk-forward, splits, regime awareness |
| `backtest-critique` | Tear apart a claimed edge |
| `model-card` | What a model is allowed to claim |
| `experiment-log` | Reproducible run records |

### Market layer

| Skill ID | Job |
|---|---|
| `market-data-hygiene` | Lines, open/close, vig, missingness |
| `clv-evaluation` | Closing-line / market-relative evaluation |
| `calibration-check` | Probability quality vs outcomes |

### Later

- comms: `edge-writeup`, `anti-slop-analytics`
- sport modules only after core is stable, equal-class candidates:
  - NFL / college football
  - MLB / baseball
  - NBA / college basketball
  - NHL / hockey
  - soccer
  - golf
  - others as earned

See [docs/taxonomy.md](./docs/taxonomy.md) and [docs/roadmap.md](./docs/roadmap.md).

---

## Repository layout

```text
sports-analytic-skills/
├── README.md
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── LICENSE
├── plugin.json
├── docs/
│   ├── roadmap.md
│   ├── taxonomy.md
│   ├── getting-started.md
│   ├── skill-authoring.md
│   └── documentation-standard.md
├── templates/
│   └── skill/
│       └── SKILL.md
├── references/
│   └── prior-art.md
└── skills/                    # empty until real drafts land
    └── <skill-name>/
        ├── SKILL.md
        ├── scripts/           # optional
        ├── references/        # optional
        ├── assets/            # optional
        └── tests/             # required if scripts/ ships
```

---

## Getting started (planned)

Repo is public. Skill install is still **planned** until skills are drafted. **Do not treat skill-install commands as useful yet.**

### Intended options (after skills exist)

```bash
# standards-based installer (supported hosts)
npx skills add WalrusQuant/sports-analytic-skills

# GitHub CLI skill installer
gh skill install WalrusQuant/sports-analytic-skills

# manual / Agent Skills convention
git clone https://github.com/WalrusQuant/sports-analytic-skills.git ~/.agents/skills/sports-analytic-skills
```

### Agent Plugins clients

This repo already carries a valid-shaped [`plugin.json`](./plugin.json). Plugin clients discover immediate children of `skills/` that contain `SKILL.md`.

### Local development right now

```bash
cd projects/sports-analytic-skills
ls
# read ARCHITECTURE.md + docs/* before drafting any skill
```

Detailed host notes: [docs/getting-started.md](./docs/getting-started.md)

---

## How a skill is structured

Canonical template: [templates/skill/SKILL.md](./templates/skill/SKILL.md)

```yaml
---
name: skill-name
description: >
  What it does + when an agent should load it.
  Written for discovery, not marketing.
version: "0.1.0"
license: MIT
---
```

Required body sections:

1. When to use / when not to use
2. Required inputs
3. Procedure
4. Hard constraints
5. Anti-patterns
6. Output contract
7. Handoffs
8. Worked example
9. References

Authoring rules: [docs/skill-authoring.md](./docs/skill-authoring.md)

---

## Documentation standard

We are explicitly matching the **documentation seriousness** of packs like K-Dense, not their skill count on day one.

Public docs must answer:

| Question | Where it lives |
|---|---|
| What is this? | README |
| Why should anyone care? | README |
| How is the system designed? | ARCHITECTURE.md |
| What exists vs planned? | README status + roadmap |
| How do I install later? | docs/getting-started.md |
| How do I write a skill? | docs/skill-authoring.md |
| What does “good docs” mean here? | docs/documentation-standard.md |
| What is in/out of scope? | README + ARCHITECTURE |
| Can I trust claims? | Disclaimer + ethics skill |

Rule: **no fake completeness.** If a skill is not drafted, the docs say planned. Badges, counts, and examples must stay honest.

Full bar: [docs/documentation-standard.md](./docs/documentation-standard.md)

---

## Security and trust

Agent skills can steer models hard: they influence what code gets written, what gets trusted, and what gets refused.

Rules for this project:

- review every skill before install on a real agent
- prefer installing a topical subset over “all skills forever”
- scripts are optional and must be understandable
- no skill should require hidden network calls as a default path
- no skill should teach ToS-hostile scraping as the normal method
- treat community contributions (if/when open) as untrusted until reviewed

During private design: do not apply these skills to production agents.

---

## Disclaimer

This project provides methodological guidance for sports analytics and research automation.

It is:

- not financial advice
- not betting advice
- not a promise of profit
- not a substitute for domain expertise or local laws

You are solely responsible for how you use it. See [LICENSE](./LICENSE).

---

## Roadmap

High level:

1. Architecture + documentation standard — **in progress**
2. Foundation triad drafts (`doctrine`, `ethics`, `risk`)
3. Modeling spine drafts
4. Market layer drafts
5. Dogfood on synthetic/public data
6. Public GitHub when several skills are non-embarrassing
7. Sport modules after core is stable
8. Optional harness later

Living detail: [docs/roadmap.md](./docs/roadmap.md)

---

## Contributing

Right now this is a private craft project. Contribution rules are still written so the repo behaves like a real public library from day one.

See [CONTRIBUTING.md](./CONTRIBUTING.md).

Working rules:

1. Design in this repo; skills stay uninstalled on personal runtimes until explicitly enabled
2. Do not apply skills to a live OpenClaw instance from this project unless asked
3. Do not create Skill Workshop proposals until asked
4. Prefer fewer sharp skills over many shallow ones
5. Keep docs honest about planned vs shipped

---

## FAQ

### Is this just K-Dense with sports words?

No. We steal K-Dense’s **shape** (standards, docs depth, skill packaging, optional later harness), not its scientific domain or “ship 160 skills” scale.

### Is this a betting bot framework?

No. Modeling and evaluation first. Market tools are an evaluation layer. No autobet core.

### Which sport is first?

None. Core is sport-agnostic. Modules for NFL, MLB, NBA, NHL, soccer, golf, and others come later as equals.

### Why write a giant README before skills exist?

Because the public artifact is a library, not a vibe. If the docs are weak, the project is weak — even if a couple of markdown skills exist.

### Will this be installed into OpenClaw automatically?

No. Library repo and runtime install are separate on purpose.

### Can agents use any Python package anyway?

Yes. Skills do not replace libraries. They constrain method, evidence, and claims when doing sports modeling work.

### When is a skill “done”?

When a stranger can install it, follow it, and an agent is less likely to leak, overfit, or overclaim. See quality bar in [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## Prior art

- [K-Dense Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills)
- [Taste / design-taste-frontend](https://github.com/leonxlnx/taste-skill)
- [ds-skills](https://github.com/wenmin-wu/ds-skills)
- [Agent Skills standard](https://agentskills.io/)
- [Agent Plugins](https://agent-plugins.org/)

Notes: [references/prior-art.md](./references/prior-art.md)

---

## License

MIT. See [LICENSE](./LICENSE).

---

## Citation

If this library becomes public and useful, cite the repository:

```text
Wickwire, A. (2026). Sports Analytic Skills.
https://github.com/WalrusQuant/sports-analytic-skills
Multi-sport data science Agent Skills library.
```
