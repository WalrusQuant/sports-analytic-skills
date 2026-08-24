# Sports Analytic Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.4.0-blue.svg)](plugin.json)
[![Skills](https://img.shields.io/badge/Skills-20_drafted-brightgreen.svg)](#available-skills)
[![Status](https://img.shields.io/badge/Status-judgment_%2B_data_plane-orange.svg)](#project-status)
[![Standard](https://img.shields.io/badge/Standard-Agent_Skills-blueviolet.svg)](https://agentskills.io/)
[![Plugins](https://img.shields.io/badge/Standard-Agent_Plugins-0A7A72.svg)](https://agent-plugins.org/)
[![Works with](https://img.shields.io/badge/Target-Cursor_|_Claude_Code_|_Codex_|_OpenClaw-blue.svg)](#getting-started)

> Multi-sport data science skills for AI agents.  
> Judgment for honest modeling **and** a data plane for real loaders (nflverse, SportsDataverse, pybaseball).

**Sports Analytic Skills** is an open, free Agent Skills library for **sports modeling and sports analytics across sports**. It follows the open standards for portable agent skills:

- [Agent Skills](https://agentskills.io/) (`SKILL.md` + frontmatter discovery)
- [Agent Plugins](https://agent-plugins.org/) (`plugin.json` + `skills/`)

The goal is not another prompt dump. The goal is a **documented, installable methodology pack** any compatible agent host can load: Claude Code, Codex, Cursor, OpenClaw, and others.

---

## Project status

| Item | State |
|---|---|
| Version | 0.4.0 |
| Architecture | v0 locked (judgment + data plane) |
| Skills drafted | **20** (judgment workflows + data/package plane) |
| Skills marked ready | 0 (all still `draft`) |
| Repository | https://github.com/WalrusQuant/sports-analytic-skills |
| Release maturity | early public draft — usable as methodology files, not a polished product release |

Documentation quality is treated as part of the product. Counts and status labels stay honest: drafted is not the same as ready.

---

## Table of contents

- [Why this exists](#why-this-exists)
- [What this is](#what-this-is)
- [What this is not](#what-this-is-not)
- [Design principles](#design-principles)
- [Architecture overview](#architecture-overview)
- [What's included (repo)](#whats-included-repo)
- [Available skills](#available-skills)
- [Suggested install subsets](#suggested-install-subsets)
- [Repository layout](#repository-layout)
- [Getting started](#getting-started)
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

This project encodes that judgment as installable skills:

> Sharp multi-sport analytic discipline, packaged so an agent can follow it consistently.

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
    any Agent Skills-compatible host
    + user tools, data, and APIs (outside this repo)
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
| `skills/` | 15 drafted skill folders under `skills/` |

Each future skill is expected to include:

- comprehensive `SKILL.md` documentation
- when-to-use / when-not-to-use gates
- hard constraints and anti-patterns
- checkable output contract
- handoffs to related skills
- at least one worked example (synthetic or public data by default)
- optional `scripts/`, `references/`, `assets/`, `tests/` when earned

---

## Available skills

**Status key:** `draft` = written and in repo; not yet hardened to “ready.”  
All skills below are sport-agnostic unless later moved into a sport module.

### Catalog summary

| Domain | Count | Skills |
|---|---:|---|
| Foundation | 3 | doctrine, ethics, risk |
| Modeling | 3 | baseline-models, feature-rules, model-card |
| Validation | 3 | leakage-audit, validation-design, backtest-critique |
| Ops | 1 | experiment-log |
| Markets | 3 | market-data-hygiene, clv-evaluation, calibration-check |
| Comms | 2 | edge-writeup, anti-slop-analytics |
| Data plane | 5 | environment-setup, data-sources, nflreadpy, sportsdataverse-py, pybaseball |
| **Total drafted** | **20** | |

### Foundation (L1)

| Skill | Status | When to use | Path |
|---|---|---|---|
| **doctrine** | draft | Start work, judge edge vs noise, ship/paper/kill | [`skills/doctrine`](./skills/doctrine/SKILL.md) |
| **ethics** | draft | Claims, public wording, refuse locks/guarantees | [`skills/ethics`](./skills/ethics/SKILL.md) |
| **risk** | draft | Uncertainty, calibration posture, stake discipline language | [`skills/risk`](./skills/risk/SKILL.md) |

### Modeling spine

| Skill | Status | When to use | Path |
|---|---|---|---|
| **baseline-models** | draft | Define/beat simple baselines before complexity | [`skills/baseline-models`](./skills/baseline-models/SKILL.md) |
| **feature-rules** | draft | Build time-safe features at prediction timestamp T | [`skills/feature-rules`](./skills/feature-rules/SKILL.md) |
| **model-card** | draft | Freeze what a model may claim | [`skills/model-card`](./skills/model-card/SKILL.md) |

### Validation & critique

| Skill | Status | When to use | Path |
|---|---|---|---|
| **leakage-audit** | draft | Adversarial look-ahead/target leakage review | [`skills/leakage-audit`](./skills/leakage-audit/SKILL.md) |
| **validation-design** | draft | Walk-forward, embargoes, metric charter | [`skills/validation-design`](./skills/validation-design/SKILL.md) |
| **backtest-critique** | draft | Tear apart a claimed backtest/result | [`skills/backtest-critique`](./skills/backtest-critique/SKILL.md) |

### Ops

| Skill | Status | When to use | Path |
|---|---|---|---|
| **experiment-log** | draft | Reproducible run records and keep/discard decisions | [`skills/experiment-log`](./skills/experiment-log/SKILL.md) |

### Market layer

| Skill | Status | When to use | Path |
|---|---|---|---|
| **market-data-hygiene** | draft | Clean odds panels, open/close, vig, missingness | [`skills/market-data-hygiene`](./skills/market-data-hygiene/SKILL.md) |
| **clv-evaluation** | draft | Market-relative / closing-line evaluation | [`skills/clv-evaluation`](./skills/clv-evaluation/SKILL.md) |
| **calibration-check** | draft | Do probabilities mean what they say? | [`skills/calibration-check`](./skills/calibration-check/SKILL.md) |

### Comms

| Skill | Status | When to use | Path |
|---|---|---|---|
| **edge-writeup** | draft | Honest public/shared writeup of results | [`skills/edge-writeup`](./skills/edge-writeup/SKILL.md) |
| **anti-slop-analytics** | draft | Kill chartjunk, fake certainty, vanity dashboards | [`skills/anti-slop-analytics`](./skills/anti-slop-analytics/SKILL.md) |

### Data plane (packages + sources)

| Skill | Status | When to use | Path |
|---|---|---|---|
| **environment-setup** | draft | Install Python stack + loader deps | [`skills/environment-setup`](./skills/environment-setup/SKILL.md) |
| **data-sources** | draft | Choose nflverse / SDV / pybaseball / odds path | [`skills/data-sources`](./skills/data-sources/SKILL.md) |
| **nflreadpy** | draft | Load NFL nflverse releases in Python | [`skills/nflreadpy`](./skills/nflreadpy/SKILL.md) |
| **sportsdataverse-py** | draft | Multi-sport SportsDataverse Python loaders | [`skills/sportsdataverse-py`](./skills/sportsdataverse-py/SKILL.md) |
| **pybaseball** | draft | MLB Statcast/season table pulls | [`skills/pybaseball`](./skills/pybaseball/SKILL.md) |

Supporting docs:

- [docs/data-ecosystem.md](./docs/data-ecosystem.md)
- [docs/environment.md](./docs/environment.md)
- [requirements/python-data.txt](./requirements/python-data.txt)

### Typical end-to-end path

```text
environment-setup → data-sources → nflreadpy|sportsdataverse-py|pybaseball
  → doctrine
  → baseline-models + feature-rules
  → validation-design → leakage-audit
  → experiment-log
  → calibration-check (if probs)
  → market-data-hygiene → clv-evaluation (if odds)
  → backtest-critique / model-card
  → ethics + risk
  → edge-writeup + anti-slop-analytics
```

### Not drafted yet

- Deeper package skills (statsbombpy, odds API, R-side nflreadr/hoopR/cfbfastR)
- Sport modules (equal-class later): NFL, MLB, NBA, NHL, soccer, golf, others
- Optional harness (plan → run → critique)

See also [docs/taxonomy.md](./docs/taxonomy.md) and [docs/roadmap.md](./docs/roadmap.md).

## Suggested install subsets

When hosts support selective install, prefer subsets over “all forever”:

| Subset | Skills |
|---|---|
| Foundation only | doctrine, ethics, risk |
| Modeling core | foundation + baseline-models, feature-rules, leakage-audit, validation-design, experiment-log |
| Full offline core | modeling core + backtest-critique, model-card, calibration-check |
| Market-capable core | full offline core + market-data-hygiene, clv-evaluation |
| Publish pack | market-capable core + edge-writeup, anti-slop-analytics |
| NFL data plane | environment-setup, data-sources, nflreadpy |
| Multi-sport data plane | environment-setup, data-sources, sportsdataverse-py, pybaseball |

Install only the subset you need. Review skills before enabling them on a host.

---

## Repository layout

```text
sports-analytic-skills/
├── README.md
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── LICENSE
├── plugin.json
├── requirements/
│   └── python-data.txt
├── docs/
│   ├── roadmap.md
│   ├── taxonomy.md
│   ├── getting-started.md
│   ├── skill-authoring.md
│   ├── documentation-standard.md
│   ├── data-ecosystem.md
│   └── environment.md
├── templates/
│   └── skill/
│       └── SKILL.md
├── references/
│   └── prior-art.md
└── skills/                    # 20 drafted skills (some include scripts/)
    └── <skill-name>/
        ├── SKILL.md
        ├── scripts/           # optional
        ├── references/        # optional
        ├── assets/            # optional
        └── tests/             # required if scripts/ ships
```

---

## Getting started

Repo is public and skills are drafted as files. Host install flows still vary by client; treat commands below as supported-pattern targets, not a polished product release.

### Install options

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

### Local checkout

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills
# start with README.md, ARCHITECTURE.md, and skills/
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

1. Architecture + documentation standard — **done (v0)**
2. Foundation triad drafts — **done**
3. Modeling spine + critique/ops — **done**
4. Market layer drafts — **done**
5. Comms drafts + deep README catalog — **done**
6. Dogfood on synthetic/public data — next
7. Harden drafts to ready — next
8. Sport modules after core is stable — later
9. Optional harness — later

Living detail: [docs/roadmap.md](./docs/roadmap.md)

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

Core expectations:

1. Prefer fewer sharp skills over many shallow ones
2. Keep docs honest about planned vs shipped vs ready
3. No tip-service or autobet behavior
4. Core skills stay sport-agnostic unless the change is a declared sport module

---

## FAQ

### Is this a betting bot framework?

No. Modeling and evaluation first. Market tools are an evaluation layer. No autobet core.

### Which sport is first?

None. Core is sport-agnostic. Modules for NFL, MLB, NBA, NHL, soccer, golf, and others come later as equals.

### Why is the README this deep?

Because the public artifact is a library. Docs quality is part of the product.

### Do I have to install every skill?

No. Prefer topical subsets. See [Suggested install subsets](#suggested-install-subsets).

### Can agents use any Python package anyway?

Yes. Skills do not replace libraries. They constrain method, evidence, and claims when doing sports modeling work.

### When is a skill “ready”?

When a stranger can install it, follow it, and an agent is less likely to leak, overfit, or overclaim. See the quality bar in [ARCHITECTURE.md](./ARCHITECTURE.md).

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
