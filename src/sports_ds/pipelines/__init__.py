"""End-to-end modeling pipelines."""

from sports_ds.pipelines.mlb_elo_baseline import format_mlb_elo_report, run_mlb_elo_baseline
from sports_ds.pipelines.mlb_margin_model import format_mlb_margin_report, run_mlb_margin_pipeline
from sports_ds.pipelines.mlb_win_model import format_mlb_win_report, run_mlb_win_pipeline
from sports_ds.pipelines.nba_elo_baseline import format_nba_elo_report, run_nba_elo_baseline
from sports_ds.pipelines.nba_margin_model import format_nba_margin_report, run_nba_margin_pipeline
from sports_ds.pipelines.nba_win_model import format_nba_win_report, run_nba_win_pipeline
from sports_ds.pipelines.nfl_elo_baseline import format_elo_report, run_nfl_elo_baseline
from sports_ds.pipelines.nfl_margin_model import format_margin_report, run_nfl_margin_pipeline
from sports_ds.pipelines.nfl_win_model import format_pipeline_report, run_nfl_win_pipeline
from sports_ds.pipelines.nhl_win_model import format_nhl_win_report, run_nhl_win_pipeline
from sports_ds.pipelines.nfl_player_model import format_nfl_player_report, run_nfl_player_pipeline
from sports_ds.pipelines.team_win_rich import format_team_win_rich_report, run_team_win_rich_pipeline

__all__ = [
    "run_nfl_win_pipeline",
    "format_pipeline_report",
    "run_nfl_margin_pipeline",
    "format_margin_report",
    "run_nfl_elo_baseline",
    "format_elo_report",
    "run_nba_win_pipeline",
    "format_nba_win_report",
    "run_nba_margin_pipeline",
    "format_nba_margin_report",
    "run_nba_elo_baseline",
    "format_nba_elo_report",
    "run_mlb_win_pipeline",
    "format_mlb_win_report",
    "run_mlb_margin_pipeline",
    "format_mlb_margin_report",
    "run_mlb_elo_baseline",
    "format_mlb_elo_report",
    "run_nhl_win_pipeline",
    "format_nhl_win_report",
    "run_nfl_player_pipeline",
    "format_nfl_player_report",
    "run_team_win_rich_pipeline",
    "format_team_win_rich_report",
]
