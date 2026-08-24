# sports_ds toolkit map

Use the narrowest reusable surface that satisfies the request.

## Data

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.data.nba import load_nba_team_game_panel
from sports_ds.data.mlb import load_mlb_team_game_panel
```

NFL is included in the base toolkit dependency set. NBA and MLB loaders require
the toolkit's `multi` optional dependencies.

Player loaders live in:

- `sports_ds.data.nfl_players`
- `sports_ds.data.nba_players`
- `sports_ds.data.mlb_players`

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

Discover the current command surface rather than assuming it:

```bash
sports-ds --help
sports-ds feature-registry
```

The CLI includes EDA, team win/margin/Elo, player, calibration, and leakage
commands for supported sports. Pipeline commands are reference benchmarks, not
dependencies of the standalone skills. When a command supports `--json-out`,
write the artifact explicitly and validate its schema before downstream use.

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
