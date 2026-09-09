from pathlib import Path

import pandas as pd

from sports_ds.artifacts import win_fold_metrics_payload, write_win_skill_artifacts
from sports_ds.pipelines.team_win import run_team_win_pipeline


def _make_panel(seasons=(2022, 2023, 2024), weeks=12) -> pd.DataFrame:
    rows = []
    gid = 0
    for season in seasons:
        for week in range(1, weeks + 1):
            pairs = [("A", "B"), ("C", "D")] if week % 2 else [("A", "C"), ("B", "D")]
            for home, away in pairs:
                gid += 1
                home_pts = 20 + (3 if home in {"A", "C"} else 0) + (week % 3)
                away_pts = 18 + (week % 2)
                day = pd.Timestamp(f"{season}-01-{min(week, 28):02d}")
                rows.append(
                    {
                        "game_id": f"{season}-{gid}",
                        "season": season,
                        "week": week,
                        "gameday": day,
                        "team": home,
                        "opponent": away,
                        "is_home": 1,
                        "points_for": float(home_pts),
                        "points_against": float(away_pts),
                        "won": int(home_pts > away_pts),
                        "point_diff": float(home_pts - away_pts),
                    }
                )
                rows.append(
                    {
                        "game_id": f"{season}-{gid}",
                        "season": season,
                        "week": week,
                        "gameday": day,
                        "team": away,
                        "opponent": home,
                        "is_home": 0,
                        "points_for": float(away_pts),
                        "points_against": float(home_pts),
                        "won": int(away_pts > home_pts),
                        "point_diff": float(away_pts - home_pts),
                    }
                )
    return pd.DataFrame(rows)


def test_win_pipeline_exports_skill_artifacts(tmp_path: Path):
    panel = _make_panel()
    result = run_team_win_pipeline(
        panel,
        sport="toy",
        seasons=[2022, 2023, 2024],
        min_train_seasons=1,
        min_pre_games=1,
        min_train_rows=10,
        min_test_rows=10,
    )
    assert result["predictions"]
    assert result["folds"][0]["fold"] == str(result["folds"][0]["test_season"])
    payload = win_fold_metrics_payload(result)
    assert payload["primary_metric"] == "log_loss"
    assert payload["folds"][0]["model"] == result["folds"][0]["logistic_log_loss"]
    assert payload["folds"][0]["baseline"] == result["folds"][0]["constant_log_loss"]

    paths = write_win_skill_artifacts(result, tmp_path)
    assert paths["folds"].is_file()
    text = paths["predictions"].read_text(encoding="utf-8")
    assert "y_true" in text
    assert "p_pred" in text
    assert "fold" in text
