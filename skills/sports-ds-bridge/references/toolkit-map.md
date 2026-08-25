# sports_ds toolkit map

Use the narrowest reusable surface that satisfies the request. Discover the live
CLI with `sports-ds --help` rather than assuming this file is exhaustive.

## Data loaders

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.data.nba import load_nba_team_game_panel
from sports_ds.data.mlb import load_mlb_team_game_panel
```

NFL is included in the base toolkit dependency set. NBA and MLB loaders require
the toolkit's `multi` optional dependencies.

Player loaders:

```python
from sports_ds.data import nfl_players, nba_players, mlb_players
```

- `sports_ds.data.nfl_players`
- `sports_ds.data.nba_players`
- `sports_ds.data.mlb_players`

NHL team loaders exist but historical sportsdataverse coverage has been
unreliable. Treat NHL as explicit opt-in only.

## Reusable analysis components

| Capability | Module |
|---|---|
| Panel summaries | `sports_ds.eda` |
| Team/player form | `sports_ds.features` |
| Feature legality registry | `sports_ds.features.registry` |
| Elo | `sports_ds.ratings` |
| Baselines and estimators | `sports_ds.models` |
| Classification/calibration metrics | `sports_ds.metrics` |
| Leakage checks | `sports_ds.audit` |
| Walk-forward masks | `sports_ds.validation` |

These modules are adapters and accelerators. Export their results before
handing work to a standalone skill.

## CLI reference workflows

```bash
sports-ds --help
sports-ds feature-registry
```

### Team EDA

```bash
sports-ds nfl-eda --seasons 2023-2024
sports-ds nba-eda --seasons 2023-2024
sports-ds mlb-eda --seasons 2023-2024
# nhl-eda exists; data quality caveats apply
```

### Team benchmarks

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out artifacts/nfl_win.json
sports-ds nfl-margin-pipeline --seasons 2018-2024 --json-out artifacts/nfl_margin.json
sports-ds nfl-elo --seasons 2018-2024 --json-out artifacts/nfl_elo.json
sports-ds nfl-win-rich --seasons 2018-2024 --json-out artifacts/nfl_win_rich.json

sports-ds nba-win-pipeline --seasons 2023-2024 --json-out artifacts/nba_win.json
sports-ds nba-margin-pipeline --seasons 2023-2024 --json-out artifacts/nba_margin.json
sports-ds nba-elo --seasons 2023-2024 --json-out artifacts/nba_elo.json

sports-ds mlb-win-pipeline --seasons 2023-2024 --json-out artifacts/mlb_win.json
sports-ds mlb-margin-pipeline --seasons 2023-2024 --json-out artifacts/mlb_margin.json
sports-ds mlb-elo --seasons 2023-2024 --json-out artifacts/mlb_elo.json
```

### Player paths

```bash
sports-ds nfl-player-eda --seasons 2023-2024 --positions QB,RB,WR,TE
sports-ds nfl-player-pipeline --seasons 2022-2024 --target fantasy_points_ppr --json-out artifacts/nfl_player.json

sports-ds nba-player-eda --seasons 2023-2024
sports-ds nba-player-pipeline --seasons 2023-2024 --target fantasy_points --json-out artifacts/nba_player.json

sports-ds mlb-player-eda --seasons 2024
sports-ds mlb-player-pipeline --seasons 2023-2024 --max-games 50 --json-out artifacts/mlb_player.json
```

### Trust checks

```bash
sports-ds calibrate --sport nfl --seasons 2018-2024 --json-out artifacts/cal.json
sports-ds leakage-audit --sport nfl --seasons 2023-2024 --json-out artifacts/leak.json
```

Pipeline commands are reference benchmarks, not dependencies of the standalone
skills. When a command supports `--json-out`, write the artifact explicitly and
validate or translate its schema before downstream use.

## Handoff example

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

The downstream skill should read `data/nfl_team_games.parquet`; it should not
import the loader itself.
