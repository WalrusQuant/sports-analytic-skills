import pandas as pd

from sports_ds.models.regress import baseline_mean_margin, fit_margin_regressor


def test_margin_regressor_runs():
    df = pd.DataFrame(
        {
            "is_home": [1, 0, 1, 0, 1, 0, 1, 0],
            "x": [1, -1, 2, -2, 3, -3, 4, -4],
            "point_diff": [3, -3, 6, -6, 9, -9, 2, -2],
            "season": [2018, 2018, 2018, 2018, 2019, 2019, 2019, 2019],
        }
    )
    tr = df["season"] == 2018
    te = df["season"] == 2019
    const = baseline_mean_margin(df, tr, te)
    assert const.n == 4
    _, res, out = fit_margin_regressor(df, ["is_home", "x"], tr, te, model_type="ridge")
    assert res.n == 4
    assert "pred_margin" in out.columns
