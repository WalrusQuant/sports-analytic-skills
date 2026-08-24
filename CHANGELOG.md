# Changelog

## 0.12.0 — 2026-08-24

### Standalone skill pack

- Made all generic analytics and modeling skills usable without `sports_ds`,
  repository-relative paths, or an end-to-end pipeline.
- Added `sports-ds-bridge` as the explicit optional path from toolkit loaders,
  core APIs, CLI commands, and pipelines to portable user-owned artifacts.
- Added validated fold-metric, held-out-prediction, calibration, Elo,
  simulation, visualization, and reporting handoffs.
- Added isolated helper, boundary, negative-case, and cross-skill smoke tests.

### Toolkit and release engineering

- Eliminated pandas DataFrame-fragmentation warnings in player-form feature
  construction while preserving exact output behavior.
- Added offline CI across Python 3.10–3.13 and scheduled/manual live-data CI.
- Unified the repository, plugin, and toolkit release version at `0.12.0`.

## 0.11.1

### MLB player path to parity
- Parallel boxscore fetch + resume cache; optional full panel parquet cache
- Richer batter features: OPS/ISO/K%/BB% form, rest days, batting-order slot, opp starter K/9
- Lean proven feature set + starter filter + shrunk player baseline + hist-GBR/ridge/blend ladder
- Live dense 2023→2024 walk-forward beats constant on fantasy points (and TB/hits/PA)
- `mlb-player-pipeline` supports `--target fantasy_points|total_bases|hits|plate_appearances`

## 0.11.0

### Player paths (NBA + MLB)
- NBA player panel via bulk `load_nba_player_boxscore` + `nba-player-eda` / `nba-player-pipeline`
- MLB batter panel via cached per-game `mlb_boxscore` + `mlb-player-eda` / `mlb-player-pipeline` (`--max-games` for smokes)
- Shared player form engine + generic `pipelines/player_model.py` (NFL refactored onto it)
- Sport-specific feature defaults for NBA/MLB fantasy proxies
- Unit tests for NBA/MLB player form/pipeline; optional live player integration tests

## 0.10.0

### Package depth
- Richer team form features: EWMA, rest days, home/away split form, calendar week, offense-vs-defense proxies
- `RICH_WIN_FEATURE_COLS` + `sports-ds nfl-win-rich` (logistic / hist-gbm / form+Elo ensemble ladder)
- Form+Elo probability ensemble (`sports_ds.models.ensemble`)
- NFL player-level path: `load_player_game_panel`, player form features, `sports-ds nfl-player-pipeline` / `nfl-player-eda`
- Feature registry expanded for rich + player features
- Unit tests for rich features, ensemble, player form; optional live rich/player integration tests

## 0.9.1

### Skill depth + tests
- Full operator-manual pass across skill pack
- Heavier offline integration tests (25 passing at tag)

## 0.9.0

### Package depth
- Generic team-margin and team-Elo engines (`pipelines/team_margin.py`, `team_elo.py`)
- NBA/MLB margin + Elo CLI: `nba-margin-pipeline`, `nba-elo`, `mlb-margin-pipeline`, `mlb-elo`
- `sports-ds feature-registry`
- `calibrate` / `leakage-audit` accept `--sport nfl|nba|mlb`
- Feature registry module + unit tests (13 passing)

### Skill depth
- Raised environment-setup, sports-visualization, model-card, anti-slop, results-reporting, experiment-log, nflreadpy, model-interpretation to package-aware manuals
- Multi-sport plot scripts (`--sport`) + walk-forward metric plotter

## 0.8.0

### Multi-sport package paths
- Shared team-game panel helpers (`sports_ds.data.panel`)
- Generic team-win walk-forward engine (`sports_ds.pipelines.team_win`)
- NBA / MLB / NHL loaders + `*-eda` / `*-win-pipeline` CLI commands
- NHL corrupt-score dump detection (skips unusable seasons like constant 2-3 scores)
- Docs/skills updated for multi-sport package paths

## 0.7.0

### Package
- Add `sports_ds.ratings` as-of Elo
- Add `sports_ds.metrics` (brier, log-loss, ECE/calibration)
- Add `sports_ds.audit.leakage` package leakage audit
- Add margin regressors + `nfl-margin-pipeline`
- Add `nfl-elo` walk-forward baseline pipeline
- Add NBA loader + `nba-eda` / `nba-win-pipeline` (requires `[multi]`)
- Expand CLI: calibrate, leakage-audit, margin, elo, nba commands

### Docs
- Product charter (`docs/product-charter.md`)
- Agent runbook (`docs/agent-runbook.md`)
- Architecture + README synced to real package surface

### Tests
- Unit tests for features, splits, Elo as-of, metrics, leakage audit, regressors

## 0.6.0

- Initial public sports_ds + skill pack with NFL win pipeline and deep skill manuals
