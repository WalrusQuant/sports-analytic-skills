# Changelog

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
