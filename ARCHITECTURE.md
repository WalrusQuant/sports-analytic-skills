# Architecture — Sports Analytic Skills

**Audience:** Adam + Kirby while building  
**Status:** v0 design (2026-08-24)  
**Principle:** Steal K-Dense’s *shape*, not its *size*. Steal Taste’s *judgment encoding*, not its UI domain.

### Locked decisions (2026-08-24)

1. **Name:** `sports-analytic-skills` (keep).
2. **L1 split:** separate `doctrine`, `ethics`, and `risk` skills — not one mega file.
3. **Sport scope:** core is multi-sport data science for modeling across sports. Core stays sport-agnostic. Sport-specific modules (NFL, MLB, NBA, NHL, soccer, golf, etc.) come later as expansions — none is privileged.
4. **Center of gravity:** modeling is the core engine; sports market dynamics layer in where they fit best (eval, data hygiene, claim checks) — not as the whole identity of every skill.

---

## 1. Problem

General agents are fluent and sloppy at sports analytics:

- leak future information into features
- treat backtests as truth
- confuse model fit with market edge
- skip closing-line / calibration reality checks
- invent “systems” without kill criteria

Taste fixed “generic UI slop” with portable design constraints.  
K-Dense fixed “science workflow amnesia” with a large skill library + optional harness.

We want the sports-betting/analytics version of that: **portable judgment**.

---

## 2. Product definition

**Name:** `sports-analytic-skills`  
**Form:** open-source skill library (Agent Skills standard)  
**User:** any analyst or agent host that loads `SKILL.md` packs  
**Value:** consistent sharp methodology under automation  
**Non-goals:** tips, bankroll product, paid SaaS, live betting bot

This is a **global public library project**, not an OpenClaw private skill.

---

## 3. Layered architecture

Three layers. Only layer 1 is required for v0.

```text
┌─────────────────────────────────────────────────────────┐
│  L3  Harness (optional, later)                          │
│      plan → execute → critique → kill/ship              │
│      multi-agent or single-agent loop                   │
├─────────────────────────────────────────────────────────┤
│  L2  Workflow skills                                    │
│      data hygiene, features, backtest, CLV, bankroll…   │
├─────────────────────────────────────────────────────────┤
│  L1  Doctrine + contracts                               │
│      what edge is, forbidden moves, ship/kill gates     │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  Host runtime (Claude Code, Codex, Cursor, OpenClaw…)   │
│  + user data/tools/MCP (not owned by this repo)         │
└─────────────────────────────────────────────────────────┘
```

### L1 — Foundation triad (split on purpose)

Three small skills every workflow skill assumes. Split so agents load only what the job needs.

| Skill | Owns |
|---|---|
| `doctrine` | What counts as analytic edge vs noise; evidence hierarchy; ship / paper-only / kill criteria; how work is judged |
| `ethics` | Honesty bounds: no fake certainty, no guaranteed-+EV language, disclosure, refuse tip-shop / lock-of-day requests, not-advice posture |
| `risk` | Uncertainty, calibration framing, stake/bankroll *discipline language* (not a bankroll product), ruin awareness, when not to size up |

This triad is the “taste dial” of the system. Without it, workflow skills become cookbook slop.

### L2 — Workflow skills

Narrow, composable procedures. Each skill:

- triggers on a clear job (“evaluate this backtest”, “build walk-forward”)
- states inputs, outputs, failure modes
- includes checklists and anti-patterns
- may ship optional scripts/templates later
- never depends on a specific bookmaker UI if avoidable

### L3 — Harness (deferred)

Only after L1+L2 are sharp enough that a weak model still can’t easily cheat:

- planner proposes analysis plan under doctrine
- executor runs code/tools
- critic checks leakage, CLV, calibration, stake claims
- result is accept / revise / kill

Harness is **not** the v0 deliverable. Skills must stand alone first.

---

## 4. Skill unit design

Each skill is a directory:

```text
skills/<skill-name>/
├── SKILL.md              # required
├── scripts/              # optional deterministic helpers
├── references/           # optional deeper notes
├── assets/               # optional templates, diagrams
└── tests/                # optional if scripts exist
```

### SKILL.md contract

```yaml
---
name: skill-name
description: >
  One/two sentences: what it does + WHEN to use it.
  Written for agent discovery, not marketing.
version: "0.1.0"
license: MIT
---
```

Body sections (standard for this repo):

1. **When to use / when not to use**
2. **Required inputs**
3. **Procedure** (ordered steps an agent can follow)
4. **Hard constraints** (non-negotiables)
5. **Anti-patterns** (common failure modes)
6. **Output contract** (what “done” looks like)
7. **Handoffs** (which other skills to call next)
8. **References** (methods, papers, prior art)

### Design rules for every skill

| Rule | Why |
|---|---|
| Opinionated defaults | Vague skills reproduce slop |
| Explicit refusals | Agents need permission to stop |
| Sport-agnostic core, sport modules optional | Avoid 30 half-baked league packs |
| No “guaranteed +EV” language | Integrity + honesty |
| Scripts are helpers, not the skill | Judgment stays in markdown |
| Small enough to load | Discovery dies if every skill is a novel |

---

## 5. Proposed skill taxonomy (v0 map)

Not all exist yet. This is the architecture map, not a promise to build 50 skills.

### Center of gravity: modeling first

The library’s spine is **how to model sports outcomes honestly**, not how to scrape books.

```text
 modeling engine (core)
   baselines → features → validation → leakage → backtest critique
        │
        └── market layer (where it earns a slot)
              odds hygiene → vig → CLV / market eval → claim limits
```

Market skills are first-class, but they attach at the right joints (evaluation + data contracts), not as a wrapper that turns every skill into “betting content.”

### Tier 0 — Foundation + modeling spine (build first)

| ID | Skill | Job |
|---|---|---|
| `doctrine` | Analytic doctrine | Edge vs noise, evidence hierarchy, ship/kill |
| `ethics` | Ethics & honesty | Claims, refusals, anti-snake-oil |
| `risk` | Risk framing | Calibration language, uncertainty, stake discipline |
| `baseline-models` | Strong baselines first | Beat dumb baselines before complexity |
| `feature-rules` | Feature rules (sport-agnostic) | Legal features, time-safety, target leakage |
| `leakage-audit` | Leakage & look-ahead audit | Feature/time integrity review |
| `validation-design` | Validation design | Walk-forward, splits, regime awareness |
| `backtest-critique` | Backtest critique | Tear apart a claimed edge |
| `experiment-log` | Experiment logging | Reproducible run records |
| `model-card` | Model / claim card | What the model is allowed to claim |

### Tier 1 — Market layer (layer in where it fits)

| ID | Skill | Job |
|---|---|---|
| `market-data-hygiene` | Odds/market data hygiene | Lines, open/close, vig, missingness |
| `clv-evaluation` | Closing-line / market eval | Market-relative performance |
| `calibration-check` | Calibration check | Prob quality vs outcomes (pairs with `risk`) |

### Tier 2 — Sport modules (later only, multi-sport)

This library is for **all sports modeling**, not one league’s pet project.

Core pack stays sport-agnostic for its whole life. Sport modules are additive expansions later — same tier, no favorite child.

Planned expansion surface (order undecided; none privileged):

- NFL / college football
- MLB / baseball
- NBA / college basketball
- NHL / hockey
- soccer
- golf
- others as earned

Example module *shapes* (not a build queue, not a priority list):

- `nfl-team-strength-basics`
- `mlb-run-expectancy-basics`
- `nba-pace-adjusted-basics`
- `nhl-goalie-separation-basics`
- `soccer-xg-context`
- `golf-stroke-gained-context`

Rule: a sport module ships only if it encodes **domain constraints the core cannot express**, not wiki trivia or personal hobby bias.

### Tier 3 — Communication

| ID | Skill | Job |
|---|---|---|
| `edge-writeup` | Edge writeup | Honest public/post-ready summary |
| `anti-slop-analytics` | Analytics anti-slop | Kill hype charts and fake certainty |

### Explicitly out of scope (forever or long time)

- Bet placement bots / book account automation
- “Locks of the day”
- Bankroll product / payments
- Scraping that violates ToS as a taught default
- Guaranteed profit systems

---

## 6. Runtime & distribution architecture

```text
                    ┌──────────────────────┐
                    │  this git repo       │
                    │  (source of truth)   │
                    └──────────┬───────────┘
                               │ publish (later)
                               ▼
                    ┌──────────────────────┐
                    │  GitHub public repo  │
                    │  + plugin.json       │
                    └──────────┬───────────┘
                               │ install
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   Claude Code             Cursor               OpenClaw
   ~/.agents/skills        project skills       workspace skills
```

**Important separation:**

- **Library repo** (this project) = global artifact
- **Any one agent install** = optional consumer
- OpenClaw may eventually install selected skills, but that is a later deliberate act — not part of scaffolding

No Skill Workshop apply. No live gateway skill registration during design.

---

## 7. Relationship to tools / MCP / data

Skills are **procedure + judgment**. They are not the data plane.

```text
[User question]
    → host discovers skill via description frontmatter
    → agent reads SKILL.md
    → agent uses whatever tools exist (code exec, DB, ESPN MCP, files…)
    → skill constraints still bind the work
```

This repo may later include:

- reference schemas for odds panels
- example notebooks (synthetic data only by default)
- validation scripts

It should **not** require Adam’s private pipelines to understand a skill.

---

## 8. Quality bar (definition of done per skill)

A skill is ready to merge when:

1. Frontmatter description is discovery-grade (clear trigger)
2. A junior agent can follow procedure without improvising forbidden steps
3. Anti-patterns cover the top 5 real failure modes
4. Output contract is checkable
5. It does not assume live bankroll or paid APIs
6. It has at least one worked example (synthetic OK)
7. Adam would trust it on X as free useful craft

---

## 9. Build order (architecture sequence)

1. Freeze architecture + locked decisions (this doc) — done
2. Skill template + contribution rules — mostly done
3. Write L1 triad drafts: `doctrine`, `ethics`, `risk`
4. Write modeling spine: `baseline-models`, `feature-rules`, `leakage-audit`, `validation-design`
5. Write critique/output: `backtest-critique`, `model-card`, `experiment-log`
6. Layer market skills: `market-data-hygiene`, `clv-evaluation`, `calibration-check`
7. Dogfood on synthetic or public historical data (no private bankroll required)
8. Publish repo when ~5–8 skills are non-embarrassing
9. Multi-sport modules (NFL/MLB/NBA/NHL/soccer/golf/etc.) only after core is stable — no single-sport favoritism
10. Optional harness only after public skills stabilize

Work style: bite-sized sessions (including during work breaks). No big-bang.

---

## 10. Remaining open questions

Still open; do not block drafts on them.

1. **Quant depth in v0:** frequentist-first vs light Bayesian defaults in `risk` / validation
2. **How early to require CLV** in `backtest-critique` handoffs (hard gate vs optional when no market data)
3. **X cadence:** skill-by-skill posts only after a skill is real
4. **Contribution style later:** solo craft vs eventual external PRs

---

## 11. Success metrics (project, not betting P&L)

- Skills are installable by a stranger without our private context
- Agents following skills produce fewer leaked/overfit analyses in spot checks
- Each published skill stands alone as a useful public artifact
- Project stays fun and small enough to touch during normal life
- No pressure to monetize or “run a system” live

Betting P&L is **not** a success metric for this library.
