import pandas as pd

from sports_ds.pipelines.team_margin import run_team_margin_pipeline


def _toy_panel() -> pd.DataFrame:
    rows = []
    for season in (2023, 2024):
        for week in range(1, 12):
            gid = f"{season}-{week}"
            # A home vs B
            rows.append(
                {
                    "game_id": gid,
                    "season": season,
                    "week": week,
                    "gameday": pd.Timestamp(f"{season}-01-{week:02d}"),
                    "team": "A",
                    "opponent": "B",
                    "is_home": 1,
                    "points_for": 10 + week,
                    "points_against": 8,
                    "won": 1,
                    "point_diff": 2 + week,
                }
            )
            rows.append(
                {
                    "game_id": gid,
                    "season": season,
                    "week": week,
                    "gameday": pd.Timestamp(f"{season}-01-{week:02d}"),
                    "team": "B",
                    "opponent": "A",
                    "is_home": 0,
                    "points_for": 8,
                    "points_against": 10 + week,
                    "won": 0,
                    "point_diff": -(2 + week),
                }
            )
    return pd.DataFrame(rows)


def test_team_margin_pipeline_toy():
    panel = _toy_panel()
    result = run_team_margin_pipeline(
        panel,
        sport="toy",
        seasons=[2023, 2024],
        min_train_seasons=1,
        min_pre_games=1,
        min_train_rows=5,
        min_test_rows=5,
    )
    assert result["rows_raw_panel"] == len(panel)
    assert "mean_metrics" in result
