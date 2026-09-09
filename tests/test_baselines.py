import pandas as pd

from sports_ds.models.baselines import baseline_constant_rate, baseline_home_rate


def _panel() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "won": [1, 0, 1, 0, 1, 0],
            "is_home": [1, 0, 1, 0, 1, 0],
        }
    )


def test_constant_rate_is_overall_train_mean():
    df = _panel()
    train = df.index < 4
    test = df.index >= 4
    result = baseline_constant_rate(df, train, test)
    assert result.name == "constant_train_win_rate"
    # train won mean is 0.5 on a doubled panel
    assert abs(result.brier - 0.25) < 1e-9


def test_home_rate_uses_home_rows_then_complements_away():
    df = pd.DataFrame(
        {
            "won": [1, 0, 1, 0, 1, 0],
            "is_home": [1, 0, 1, 0, 1, 0],
        }
    )
    train = df.index < 4
    test = df.index >= 4
    result = baseline_home_rate(df, train, test)
    assert result.name == "home_train_win_rate"
    # train home rows both won -> p_home=1, away gets 0; test is home win + away loss
    assert result.accuracy == 1.0
