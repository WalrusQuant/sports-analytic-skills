import numpy as np
import pandas as pd

from sports_ds.models.ensemble import average_probs, fit_form_elo_ensemble
from sports_ds.features.team_form import DEFAULT_WIN_FEATURE_COLS, add_pregame_form_features
from sports_ds.ratings.elo import add_elo_asof


def test_average_probs_weighted():
    p = average_probs({"a": np.array([0.2, 0.8]), "b": np.array([0.4, 0.6])}, {"a": 1, "b": 1})
    assert np.allclose(p, [0.3, 0.7])


def test_form_elo_ensemble_runs():
    # multi-season toy so train/test masks work
    rows = []
    for season in (2020, 2021):
        for week in range(1, 9):
            gid = f"{season}_{week}"
            day = pd.Timestamp(year=season, month=9, day=min(week, 28))
            rows.append(
                {
                    "game_id": gid,
                    "season": season,
                    "week": week,
                    "gameday": day,
                    "team": "A",
                    "opponent": "B",
                    "is_home": 1,
                    "points_for": 24,
                    "points_against": 17,
                    "won": 1,
                    "point_diff": 7,
                }
            )
            rows.append(
                {
                    "game_id": gid,
                    "season": season,
                    "week": week,
                    "gameday": day,
                    "team": "B",
                    "opponent": "A",
                    "is_home": 0,
                    "points_for": 17,
                    "points_against": 24,
                    "won": 0,
                    "point_diff": -7,
                }
            )
    panel = pd.DataFrame(rows)
    df = add_elo_asof(add_pregame_form_features(panel))
    cols = [c for c in DEFAULT_WIN_FEATURE_COLS if c in df.columns]
    df = df.dropna(subset=cols + ["won", "elo_diff"])
    tr = df["season"] == 2020
    te = df["season"] == 2021
    _, res, prob = fit_form_elo_ensemble(df, cols, tr, te)
    assert res.n > 0
    assert 0 < res.log_loss < 2
    assert len(prob) == res.n
