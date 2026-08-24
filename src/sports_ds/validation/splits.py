"""Time-safe validation splits for sports."""

from __future__ import annotations

from collections.abc import Iterator

import pandas as pd


def season_walk_forward_masks(
    df: pd.DataFrame,
    min_train_seasons: int = 2,
) -> Iterator[tuple[int, pd.Series, pd.Series]]:
    """
    Yield (test_season, train_mask, test_mask).

    Train on all seasons < test_season. Requires at least min_train_seasons prior.
    """
    if "season" not in df.columns:
        raise ValueError("df must include season")
    seasons = sorted(int(s) for s in df["season"].dropna().unique())
    for i, test_season in enumerate(seasons):
        train_seasons = seasons[:i]
        if len(train_seasons) < min_train_seasons:
            continue
        train_mask = df["season"].isin(train_seasons)
        test_mask = df["season"] == test_season
        if train_mask.sum() == 0 or test_mask.sum() == 0:
            continue
        yield test_season, train_mask, test_mask
