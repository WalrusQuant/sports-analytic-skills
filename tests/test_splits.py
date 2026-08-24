import pandas as pd

from sports_ds.validation.splits import season_walk_forward_masks


def test_season_walk_forward_masks_order():
    df = pd.DataFrame(
        {
            "season": [2018, 2018, 2019, 2019, 2020, 2020],
            "x": range(6),
        }
    )
    folds = list(season_walk_forward_masks(df, min_train_seasons=2))
    assert len(folds) == 1
    test_season, tr, te = folds[0]
    assert test_season == 2020
    assert set(df.loc[tr, "season"].unique()) == {2018, 2019}
    assert set(df.loc[te, "season"].unique()) == {2020}
