"""End-to-end modeling pipelines."""

from sports_ds.pipelines.nba_win_model import format_nba_win_report, run_nba_win_pipeline
from sports_ds.pipelines.nfl_elo_baseline import format_elo_report, run_nfl_elo_baseline
from sports_ds.pipelines.nfl_margin_model import format_margin_report, run_nfl_margin_pipeline
from sports_ds.pipelines.nfl_win_model import format_pipeline_report, run_nfl_win_pipeline

__all__ = [
    "run_nfl_win_pipeline",
    "format_pipeline_report",
    "run_nfl_margin_pipeline",
    "format_margin_report",
    "run_nfl_elo_baseline",
    "format_elo_report",
    "run_nba_win_pipeline",
    "format_nba_win_report",
]
