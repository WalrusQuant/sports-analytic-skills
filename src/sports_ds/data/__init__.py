"""Sports data loaders."""

from sports_ds.data.nfl import load_schedules, load_team_game_panel
from sports_ds.data.nfl_players import load_player_game_panel, load_player_stats

__all__ = [
    "load_schedules",
    "load_team_game_panel",
    "load_player_stats",
    "load_player_game_panel",
]
