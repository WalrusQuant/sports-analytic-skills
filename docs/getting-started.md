# Getting started

**Status:** repository is public; skills are drafted as files. Host install UX still varies by client.

## Who this is for

- analysts building sports models with AI coding agents
- people who want portable methodology, not one-off prompts
- agent hosts that support Agent Skills / Agent Plugins

## Who this is not for

- users looking for picks
- users wanting an autobet bot
- users expecting a finished mega-library today

## Clone the repo

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills
```

Read first:

- `README.md`
- `ARCHITECTURE.md`
- `docs/skill-authoring.md`
- skills under `skills/`

## Install options

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

Do **not** install everything by default once the library grows.

Suggested topical subsets:

1. Foundation only: `doctrine`, `ethics`, `risk`
2. Modeling core: foundation + baselines/features/leakage/validation/experiment-log
3. Full offline core: modeling core + critique/model-card/calibration
4. Market-capable core: full offline core + market hygiene/CLV
5. Publish pack: market-capable core + writeup/anti-slop

## Using a skill

Compatible hosts usually:

1. discover skills from configured paths via frontmatter `description`
2. load `SKILL.md` when relevant
3. follow procedure with local tools/data

You can also invoke explicitly:

> Use the `leakage-audit` skill on this feature pipeline.

## Verify setup

- [ ] host can see skill names/descriptions
- [ ] opening one `SKILL.md` works
- [ ] agent follows when/when-not gates
- [ ] agent produces the output contract
- [ ] no unexpected network/script behavior
