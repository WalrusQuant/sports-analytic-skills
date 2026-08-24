"""NHL loaders via sportsdataverse bulk schedule releases."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from sports_ds.data.panel import as_season_list, schedule_to_team_game_panel, to_pandas
from sports_ds.data.sdv_common import MultiSportDataError, require_sportsdataverse


def _score_looks_corrupt(home_score: pd.Series, away_score: pd.Series) -> bool:
    """Detect known-bad release dumps (e.g. every game 2-3)."""
    hs = pd.to_numeric(home_score, errors="coerce")
    aws = pd.to_numeric(away_score, errors="coerce")
    ok = hs.notna() & aws.notna()
    if int(ok.sum()) < 20:
        return True
    # if almost no unique score pairs, data is not real final scores
    pairs = pd.DataFrame({"h": hs[ok], "a": aws[ok]}).drop_duplicates()
    if len(pairs) <= 2:
        return True
    # if home never wins across hundreds of games, inverted/corrupt
    home_win_rate = float((hs[ok] > aws[ok]).mean())
    if home_win_rate <= 0.05 or home_win_rate >= 0.95:
        return True
    return False


def load_nhl_schedules(seasons: int | Iterable[int] | None = None) -> pd.DataFrame:
    """Load NHL schedules/results for seasons via sportsdataverse.load_nhl_schedule.

    `seasons` are NHL end-years (2024 = 2023-24). Each requested year is labeled
    with that year for walk-forward consistency.

    Note: some SDV release seasons have corrupt constant scores (observed: 2023
    dump is all 2-3). Those seasons are skipped with an error if none remain.
    """
    require_sportsdataverse()
    from sportsdataverse.nhl import load_nhl_schedule

    season_list = as_season_list(seasons, [2023, 2024])
    frames: list[pd.DataFrame] = []
    skipped: list[str] = []
    last_err: Exception | None = None

    for season in season_list:
        try:
            try:
                raw = load_nhl_schedule(int(season), return_as_pandas=True)
            except TypeError:
                raw = load_nhl_schedule(int(season))
            df = to_pandas(raw)
            if not len(df):
                skipped.append(f"{season}:empty")
                continue
            if _score_looks_corrupt(df["home_score"], df["away_score"]):
                skipped.append(
                    f"{season}:corrupt_scores(unique_pairs_or_home_win_rate)"
                )
                continue
            if "game_state" in df.columns:
                state = df["game_state"].astype(str).str.upper()
                scored = df["home_score"].notna() & df["away_score"].notna()
                keep = state.isin(["OFF", "FINAL", "OFFICIAL"]) | scored
                df = df.loc[keep].copy()
            df = df.copy()
            df["_requested_season"] = int(season)
            frames.append(df)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            skipped.append(f"{season}:error:{type(exc).__name__}")
            continue

    if not frames:
        raise MultiSportDataError(
            "could not load usable NHL schedules for "
            f"seasons={season_list}; skipped={skipped}; last_error={last_err}. "
            "Tip: try seasons with valid SDV dumps (e.g. 2024)."
        )

    df = pd.concat(frames, ignore_index=True)
    out = pd.DataFrame(
        {
            "game_id": df["game_id"].astype(str),
            "season": pd.to_numeric(df["_requested_season"], errors="coerce").astype("Int64"),
            "gameday": pd.to_datetime(df.get("game_date"), errors="coerce"),
            "home_team": df["home_team_abbr"].astype(str),
            "away_team": df["away_team_abbr"].astype(str),
            "home_score": pd.to_numeric(df["home_score"], errors="coerce"),
            "away_score": pd.to_numeric(df["away_score"], errors="coerce"),
        }
    )
    out = out.dropna(subset=["game_id", "season", "home_team", "away_team", "home_score", "away_score"])
    out = out.drop_duplicates(subset=["game_id"], keep="first")
    out["week"] = out["gameday"].dt.isocalendar().week.astype("Int64")
    # stash skip notes on attrs for debugging
    out.attrs["skipped_seasons"] = skipped
    return out.reset_index(drop=True)


def load_nhl_team_game_panel(seasons: int | Iterable[int] | None = None) -> pd.DataFrame:
    """NHL team-game panel matching the shared panel contract."""
    return schedule_to_team_game_panel(load_nhl_schedules(seasons))
