# Sports Analytic Skills

**K-Dense-style agent skills for sports modeling and analytics.**

A portable [Agent Skills](https://agentskills.io/) / [Agent Plugins](https://agent-plugins.org/) pack: deep operator manuals, sports-specific workflows, bundled reference docs, and runnable Python scripts agents can execute. Plus an installable toolkit (`sports_ds`) the skills drive on real public sports data.

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# agent install
npx skills add WalrusQuant/sports-analytic-skills
```

---

## What each skill contains

Every skill is a folder under `skills/`:

| Piece | Purpose |
|---|---|
| `SKILL.md` | Full operator manual (workflow, code, decision tables, reporting) |
| `references/` | Deep method detail too long for the main file |
| `scripts/` | Runnable sports-specific Python helpers for agents |

This matches the structure of serious scientific agent-skill packs: **not** thin prompt stubs, **not** a project status board.

---

## Skills (23)

### Foundation

| Skill | What the agent learns to do |
|---|---|
| [`sports-modeling-doctrine`](skills/sports-modeling-doctrine/) | Lock the question, baselines, time order, and success metrics before modeling |
| [`environment-setup`](skills/environment-setup/) | Install and verify the toolkit + skill scripts |
| [`data-sources`](skills/data-sources/) | Choose public sports data ecosystems for a question |

### Data loaders

| Skill | What the agent learns to do |
|---|---|
| [`nflreadpy`](skills/nflreadpy/) | Load NFL data (nflverse) and build team-game panels |
| [`sportsdataverse-py`](skills/sportsdataverse-py/) | Multi-sport SportsDataverse loads |
| [`pybaseball`](skills/pybaseball/) | MLB Statcast and season tables |

### EDA and presentation

| Skill | What the agent learns to do |
|---|---|
| [`eda-sports`](skills/eda-sports/) | Structured sports-panel EDA before modeling |
| [`sports-visualization`](skills/sports-visualization/) | Honest sports figures for EDA and reports |
| [`anti-slop-analytics`](skills/anti-slop-analytics/) | Kill chartjunk, fake certainty, baseline erasure |

### Modeling

| Skill | What the agent learns to do |
|---|---|
| [`feature-rules`](skills/feature-rules/) | Build time-safe pre-game features |
| [`time-series-sports`](skills/time-series-sports/) | Rolling / EWMA form and ordered performance |
| [`baseline-models`](skills/baseline-models/) | Strong simple baselines before complexity |
| [`statistical-modeling`](skills/statistical-modeling/) | GLMs, diagnostics, effect sizes, hierarchical structure |
| [`predictive-modeling`](skills/predictive-modeling/) | ML under season walk-forward validation |
| [`ratings-strength-models`](skills/ratings-strength-models/) | Elo / power ratings and as-of strength |

### Validation and simulation

| Skill | What the agent learns to do |
|---|---|
| [`validation-design`](skills/validation-design/) | Season walk-forward and metric locks |
| [`leakage-audit`](skills/leakage-audit/) | Look-ahead and target leakage review |
| [`calibration-check`](skills/calibration-check/) | Probability reliability (ECE, Brier, curves) |
| [`simulation-sports`](skills/simulation-sports/) | Monte Carlo game/season projections |

### Reporting

| Skill | What the agent learns to do |
|---|---|
| [`model-interpretation`](skills/model-interpretation/) | Drivers, error slices, failure modes |
| [`results-reporting`](skills/results-reporting/) | Clear write-ups with baselines and limits |
| [`model-card`](skills/model-card/) | Durable model documentation |
| [`experiment-log`](skills/experiment-log/) | Reproducible experiment records |

---

## How an agent should work a sports problem

```text
sports-modeling-doctrine
    → data-sources + loader skill (nflreadpy / sportsdataverse-py / pybaseball)
    → eda-sports
    → feature-rules (+ time-series-sports / ratings-strength-models as needed)
    → baseline-models
    → statistical-modeling and/or predictive-modeling
    → validation-design + leakage-audit + calibration-check
    → model-interpretation → results-reporting / model-card / experiment-log
```

---

## Toolkit the skills drive (`sports_ds`)

Skills are not floating prompts. They operate real code:

```text
src/sports_ds/
  data/           # nflverse loaders, team-game panel
  eda/            # panel summaries
  features/       # shifted pre-game form features
  models/         # baselines + classifiers
  validation/     # season walk-forward splits
  pipelines/      # end-to-end NFL win model
  cli.py
```

```bash
sports-ds nfl-eda --seasons 2023-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
```

Example skill scripts:

```bash
python skills/eda-sports/scripts/panel_report.py --seasons 2023-2024
python skills/statistical-modeling/scripts/glm_diagnostics.py --seasons 2018-2023
python skills/baseline-models/scripts/run_baselines.py --seasons 2018-2024
python skills/ratings-strength-models/scripts/elo_asof.py --seasons 2018-2024
python skills/calibration-check/scripts/calibration_report.py --seasons 2018-2024
python skills/leakage-audit/scripts/audit_pregame_features.py --seasons 2023-2024
```

---

## Design rules

1. **Sports modeling first** — wins, margins, counts, ratings, form, simulation, reporting on public sports data.
2. **Time safety** — pre-game features must be knowable at decision time T; walk-forward over random game shuffles.
3. **Baselines before complexity** — constant / home / logistic form before celebrating trees.
4. **Skills drive code** — manuals point at package APIs and bundled scripts.
5. **Sport-agnostic core** — NFL is the first concrete pipeline; the skill map stays multi-sport.

---

## Docs

- [ARCHITECTURE.md](./ARCHITECTURE.md) — system layout
- [docs/getting-started.md](./docs/getting-started.md) — install and first runs
- [docs/skill-authoring.md](./docs/skill-authoring.md) — how skills in this pack are written
- [docs/taxonomy.md](./docs/taxonomy.md) — skill domains
- [docs/data-ecosystem.md](./docs/data-ecosystem.md) — public sports data sources
- [docs/environment.md](./docs/environment.md) — runtime deps

---

## License

MIT
