# Getting started

**Status:** repo is public; skills are not drafted yet. Install-as-skills is still planned.

This page exists so the install/use story is designed up front, K-Dense-style, instead of bolted on later.

## Who this is for

- analysts building sports models with AI coding agents
- people who want portable methodology, not one-off prompts
- agent hosts that support Agent Skills / Agent Plugins

## Who this is not for

- users looking for picks
- users wanting an autobet bot
- users expecting a finished 100-skill library today

## Right now (development)

```bash
cd projects/sports-analytic-skills
# read first
# README.md
# ARCHITECTURE.md
# docs/documentation-standard.md
# docs/skill-authoring.md
```

There is nothing to install into an agent runtime yet.

## After skills exist and repo is public

### Option A — standards installer

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

Confirm current host behavior in that host’s docs.

### Option B — GitHub CLI

```bash
gh skill install WalrusQuant/sports-analytic-skills
gh skill install WalrusQuant/sports-analytic-skills doctrine
```

### Option C — manual Agent Skills paths

```bash
# user-level
git clone https://github.com/WalrusQuant/sports-analytic-skills.git ~/.agents/skills/sports-analytic-skills

# project-level
git clone https://github.com/WalrusQuant/sports-analytic-skills.git .agents/skills/sports-analytic-skills
```

### Option D — Agent Plugins clients

Use root `plugin.json` + `skills/*/SKILL.md` discovery.

Cursor-style local plugin symlink pattern:

```bash
mkdir -p ~/.cursor/plugins/local
ln -s "$(pwd)" ~/.cursor/plugins/local/sports-analytic-skills
```

Reload the client and confirm skills appear.

## Recommended install shape

Do **not** install everything forever by default once the library grows.

Suggested topical subsets:

1. Foundation only: `doctrine`, `ethics`, `risk`
2. Modeling spine: foundation + baselines/features/leakage/validation/critique
3. Full core: modeling spine + market layer
4. Core + one sport module

## Using a skill

Compatible hosts usually:

1. discover skills from configured paths via frontmatter `description`
2. load `SKILL.md` when relevant
3. follow procedure with local tools/data

You can also invoke explicitly:

> Use the `leakage-audit` skill on this feature pipeline.

## Local OpenClaw note

This repository is a **global library project**.  
Installing into a personal OpenClaw instance is optional, deliberate, and not part of early design work.

## Verify setup (future checklist)

- [ ] host can see skill names/descriptions
- [ ] opening one `SKILL.md` works
- [ ] agent follows when/when-not gates
- [ ] agent produces the output contract
- [ ] no unexpected network/script behavior
