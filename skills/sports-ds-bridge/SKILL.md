---
name: sports-ds-bridge
description: >
  Connect the optional sports_ds Python toolkit to the standalone sports
  analytics skills. Use when the user explicitly mentions sports_ds, wants its
  NFL/NBA/MLB public-data loaders or CLI, needs toolkit setup/troubleshooting,
  or wants to convert toolkit output into a skill's documented input artifact.
license: MIT
metadata:
  version: "0.12.0"
---

# Sports DS Bridge

## Overview

`sports_ds` is an optional data and workflow accelerator that lives in the same
repository as this skill pack. It is **not** required by the other skills.

This bridge is the only skill allowed to talk about `sports_ds` setup, imports,
CLI commands, caches, and pipeline outputs. Its job is narrow:

1. decide whether the toolkit is actually needed;
2. set it up only with authorization;
3. use the narrowest toolkit surface that satisfies the request;
4. materialize a **portable** CSV / Parquet / JSON artifact;
5. validate that artifact against the downstream skill's own contract;
6. hand off to a standalone skill and stop.

The bridge is an integration boundary, not a second modeling stack. After the
handoff, generic skills must not call back into `sports_ds`.

Read [references/toolkit-map.md](references/toolkit-map.md) for concrete imports
and CLI routes. Read [references/handoff-contracts.md](references/handoff-contracts.md)
before writing an artifact for another skill.

---

## When to Use This Skill

Use this skill when:

- the user explicitly names `sports_ds`, `sports-ds`, or this repository's toolkit;
- the user wants the optional public-data loaders / normalized panels for
  NFL, NBA, or MLB;
- the user wants toolkit CLI reference pipelines or feature-registry output;
- the user needs setup, install, import, cache, or CLI troubleshooting for the toolkit;
- the user already has toolkit output and needs it translated into a portable
  artifact another skill can consume.

Do **not** use this skill when:

- the user already has usable CSV / Parquet / JSON and just wants EDA, features,
  models, validation, calibration, or reporting;
- a public loader skill (`nflreadpy`, `sportsdataverse-py`, `pybaseball`,
  `data-sources`) is enough and the user did not ask for the toolkit;
- you are tempted to make a generic skill "easier" by smuggling in a
  `sports_ds` dependency;
- the request is custom betting-market construction, pick selling, or claimed edge.

| Need | Prefer instead |
|---|---|
| Ordinary EDA on user data | `eda-sports` |
| Feature legality / leakage | `feature-rules`, `leakage-audit` |
| Baselines / predictive models | `baseline-models`, `predictive-modeling` |
| Public NFL load without toolkit | `nflreadpy` |
| Public MLB load without toolkit | `pybaseball` |
| Multi-sport source choice | `data-sources` / `sportsdataverse-py` |
| Environment only | `environment-setup` |

---

## Installation

The toolkit is optional. Confirm it is missing before suggesting install, and
get authorization before cloning or installing.

### Check first

```bash
python -c "import sports_ds; print(sports_ds.__version__)"
sports-ds --help
```

If import works, do not reinstall. Record the version and continue.

### Authorized install from the public repo

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .
```

Optional multi-sport loaders (NBA/MLB via sportsdataverse / pybaseball):

```bash
python -m pip install -e ".[multi]"
```

Optional developer/test extras:

```bash
python -m pip install -e ".[dev]"
```

Compatibility notes:

- Python 3.10+ required.
- Base install covers NFL (`nflreadpy`) and the scientific stack.
- NBA/MLB team and player loaders need `.[multi]`.
- On macOS only, XGBoost pulled by sportsdataverse may need OpenMP:
  `brew install libomp`. Not required for skill-only installs and usually
  unnecessary on Linux.
- Keep installs inside a project venv. Do not modify system Python.
- Large public-data pulls and caches need explicit user authorization.

---

## Decision workflow

Every bridge task follows this arc. Do not skip.

1. **Name the downstream skill and its contract.**
   - What skill will consume the artifact?
   - What grain, keys, and required fields does that skill document?
   - If the contract is unknown, stop and open that skill first.

2. **Decide whether `sports_ds` is necessary.**
   - User already has the table → skip the toolkit; hand the path to the skill.
   - User wants public data only → prefer loader skills unless they asked for the toolkit.
   - User asked for `sports_ds` / reference pipelines / normalized panels → continue.

3. **Check importability before setup.**
   - Import + `sports-ds --help` first.
   - Install only with authorization when missing.

4. **Choose the narrowest surface.**
   - Loader/core API for data or one transform.
   - CLI pipeline only when the user wants an end-to-end reference benchmark.
   - Never default to the heaviest pipeline "to be helpful."

5. **Materialize a portable artifact in the user's project.**
   - CSV / Parquet / JSON owned by the user.
   - Stable path under their workspace (`data/`, `artifacts/`, etc.).
   - No reliance on repo-relative paths or pipeline provenance.

6. **Validate before handoff.**
   - Required columns present.
   - Grain correct (team-game doubled? one row per decision? unique game ids?).
   - Time fields usable for walk-forward.
   - Missingness and row counts sane for the claimed window.

7. **Hand off and stop.**
   - Tell the agent which standalone skill to run next.
   - Do not keep modeling inside the bridge.
   - Do not tell the next skill to import `sports_ds`.

---

## Choose the narrowest toolkit surface

| Need | Prefer | Avoid unless requested |
|---|---|---|
| NFL schedules / team-game panel | `sports_ds.data.nfl` | full win pipeline |
| NBA / MLB team-game panel | `sports_ds.data.nba` / `.mlb` | unrelated model pipeline |
| Player-game panels | matching `sports_ds.data.*_players` | team pipeline as substitute |
| Time-safe form features | `sports_ds.features` | copying pipeline internals |
| Feature legality catalog | `sports-ds feature-registry` | inventing column meanings |
| Elo ratings | `sports_ds.ratings` | end-to-end CLI run |
| Metrics / splits / leakage helpers | matching core module | pipeline-owned constants |
| Reproducible reference benchmark | `sports-ds` CLI pipeline + `--json-out` | treating output as universal schema |

### Loader-first pattern (preferred)

```python
from pathlib import Path
from sports_ds.data.nfl import load_team_game_panel

panel = load_team_game_panel([2022, 2023, 2024])
required = {
    "season", "game_id", "gameday", "team", "opponent", "is_home",
    "points_for", "points_against", "point_diff", "won",
}
missing = sorted(required.difference(panel.columns))
if missing:
    raise ValueError(f"team-game panel missing columns: {missing}")

out = Path("data/nfl_team_games.parquet")
out.parent.mkdir(parents=True, exist_ok=True)
panel.to_parquet(out, index=False)
print(out)
```

Then:

```text
Use eda-sports on data/nfl_team_games.parquet. Confirm grain, coverage,
missingness, target balance, and modeling red flags.
```

### CLI reference pattern (only when asked)

Discover the live surface; do not memorize a stale subset:

```bash
sports-ds --help
sports-ds feature-registry
```

Common reference commands:

```bash
# Team EDA
sports-ds nfl-eda --seasons 2023-2024
sports-ds nba-eda --seasons 2023-2024
sports-ds mlb-eda --seasons 2023-2024

# Team walk-forward benchmarks
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out artifacts/nfl_win.json
sports-ds nfl-margin-pipeline --seasons 2018-2024 --json-out artifacts/nfl_margin.json
sports-ds nfl-elo --seasons 2018-2024 --json-out artifacts/nfl_elo.json
sports-ds nfl-win-rich --seasons 2018-2024 --json-out artifacts/nfl_win_rich.json

sports-ds nba-win-pipeline --seasons 2023-2024 --json-out artifacts/nba_win.json
sports-ds mlb-win-pipeline --seasons 2023-2024 --json-out artifacts/mlb_win.json

# Player paths
sports-ds nfl-player-eda --seasons 2023-2024
sports-ds nfl-player-pipeline --seasons 2022-2024 --target fantasy_points_ppr --json-out artifacts/nfl_player.json
sports-ds nba-player-pipeline --seasons 2023-2024 --json-out artifacts/nba_player.json
sports-ds mlb-player-pipeline --seasons 2023-2024 --max-games 50 --json-out artifacts/mlb_player.json

# Trust checks inside the toolkit (still optional)
sports-ds calibrate --sport nfl --seasons 2018-2024 --json-out artifacts/cal.json
sports-ds leakage-audit --sport nfl --seasons 2023-2024 --json-out artifacts/leak.json
```

Pipeline JSON is a **reference benchmark**, not a silent schema for
`results-reporting` or `model-card`. Translate keys explicitly or keep the
benchmark self-contained and summarize it in plain language.

NHL note: historical sportsdataverse dumps have been unreliable. Prefer
NFL/NBA/MLB unless the user explicitly accepts NHL limitations.

---

## Handoff contracts

Bridge defaults live in
[references/handoff-contracts.md](references/handoff-contracts.md).
The downstream skill remains the source of truth.

Minimum checks before handoff:

### Team-game panel

- one row per team per game (usually two complementary rows per `game_id`);
- required fields present: `season`, `game_id`, `gameday`, `team`, `opponent`,
  `is_home`, `points_for`, `points_against`, `point_diff`, `won`;
- `won` is binary from the focal team's view;
- include `week` or another within-season order field when available.

### Prediction table

- one row per evaluated decision;
- stable keys + `y_true` + `y_pred` or `p_pred`;
- time/fold field such as `season`;
- no silent renames.

### Fold-metrics JSON

- task, validation design, primary metric, per-fold n and scores;
- baseline comparison included when the benchmark claims improvement;
- map toolkit-specific keys before a reporting skill consumes them.

### Elo / simulation schedule

- one row per remaining matchup (not a doubled team panel);
- unique `game_id`;
- `team`, `opponent`, `is_home`, and either `win_probability` or documented
  ratings sufficient to compute it.

If validation fails, fix or rebuild the artifact. Do not hand garbage downstream
and hope the next skill invents columns.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: sports_ds` | toolkit not installed in active env | authorized editable install in project venv |
| `sports-ds: command not found` | scripts path / env not active | activate venv; reinstall editable; use `python -m sports_ds.cli` if needed |
| NBA/MLB import or loader fails | missing `.[multi]` | `pip install -e ".[multi]"` after approval |
| macOS native/OpenMP error | XGBoost/runtime prerequisite | `brew install libomp` or avoid multi path |
| Empty / tiny panel | season string, filters, or provider coverage | print seasons requested, row counts, date min/max |
| Pipeline JSON confuses reporting skill | schema mismatch | translate to portable fold-metrics object |
| Generic skill starts importing sports_ds | boundary violation | stop; export artifact; resume with standalone skill |
| User wanted "just EDA" | wrong skill | leave bridge; use `eda-sports` on their file |
| Cache / re-download surprises | provider cache behavior | disclose cache location and freshness; get approval for large pulls |

Capture command, environment, package versions, and the exact error before
changing dependencies.

---

## Anti-patterns

| Anti-pattern | Why it fails | Correct behavior |
|---|---|---|
| Install toolkit for every sports question | turns optional accel into hidden dependency | install only when needed and authorized |
| Tell `eda-sports` to `import sports_ds` | breaks skill-only installs | export portable file, then hand off |
| Treat pipeline JSON as universal schema | reporting lies about design/metrics | explicit mapping or self-contained summary |
| Run richest pipeline by default | slow, opaque, over-scoped | loader/core first; pipeline on request |
| Skip column validation | downstream skill fails mysteriously | validate required fields before handoff |
| Use doubled team panel as simulation schedule | double-counts games | one row per matchup |
| Claim toolkit output has betting edge | false product claim | report methodology and limits only |
| Quietly broaden seasons/network pulls | cost, policy, and reproducibility issues | bounded request + authorization |

---

## Hard constraints

1. Never imply `sports_ds` is installed merely because this skill exists.
2. Never tell a generic skill to import `sports_ds` or call `sports-ds`.
3. Never present pipeline-specific field names as a universal schema.
4. Do not install packages, download large datasets, or overwrite artifacts
   without authorization.
5. Preserve decision-time integrity on pre-game features: every value must be
   knowable at or before the declared prediction time.
6. Prefer user-owned artifact paths over repository-internal paths.
7. NHL remains second-class until data quality is explicitly accepted.
8. No odds/EV/arbitrage product claims. This bridge does not sell picks.

---

## Worked paths

### A. User wants NFL team-game data, then EDA

1. Confirm they asked for toolkit or accept it as the data path.
2. Check import; install only if missing and approved.
3. Load panel for a bounded season window.
4. Validate team-game required columns and 2 rows per game.
5. Write `data/nfl_team_games.parquet`.
6. Hand off to `eda-sports`.

### B. User wants a reference NFL win benchmark

1. Confirm they want the reference pipeline, not just data.
2. Run `sports-ds nfl-win-pipeline --seasons ... --json-out artifacts/nfl_win.json`.
3. Summarize fold metrics, baseline comparison, n, and limits in plain language.
4. If they want deeper interpretation, translate metrics into a portable JSON
   and open `results-reporting` / `model-card` with explicit schema notes.
5. Do not pretend the benchmark is a production betting model.

### C. User already has toolkit output and wants calibration help

1. Inspect the artifact columns.
2. Map to `y_true`, `p_pred`, and a fold/time column.
3. Write a clean predictions table.
4. Hand off to `calibration-check`.
5. Keep all sports_ds talk inside this bridge.

---

## Output contract

Finish every bridge task with:

- whether `sports_ds` was needed and why;
- toolkit version / env notes when used;
- the exact surface used (module import vs CLI command);
- artifact path, format, grain, and time window;
- required-column validation result (pass/fail + missing fields);
- row counts and any provenance/cache limitations;
- the standalone skill that should run next;
- what was **not** done (no silent modeling, no edge claim).

If the toolkit was not used, say so explicitly and point to the correct skill.
