"""MLB player-game loading via sportsdataverse per-game boxscores (cached)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Iterable

import pandas as pd

from sports_ds.data.mlb import load_mlb_schedules
from sports_ds.data.panel import as_season_list, to_pandas
from sports_ds.data.sdv_common import MultiSportDataError, require_sportsdataverse


DEFAULT_CACHE_DIR = Path("data/cache/mlb_boxscores")


def _boxscore_path(cache_dir: Path, game_pk: str) -> Path:
    return cache_dir / f"{game_pk}.parquet"


def load_mlb_boxscore_game(game_pk: int | str, *, cache_dir: Path | None = None) -> pd.DataFrame:
    """Load one MLB boxscore; cache parquet when cache_dir set."""
    require_sportsdataverse()
    from sportsdataverse import mlb

    gpk = str(int(float(game_pk)))
    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        path = _boxscore_path(cache_dir, gpk)
        if path.exists():
            return pd.read_parquet(path)

    raw = mlb.mlb_boxscore(int(gpk))
    df = to_pandas(raw)
    df["game_id"] = gpk
    if cache_dir is not None and len(df):
        df.to_parquet(_boxscore_path(cache_dir, gpk), index=False)
    return df


def load_mlb_player_boxscores(
    seasons: int | Iterable[int] | None = None,
    *,
    cache_dir: str | Path | None = DEFAULT_CACHE_DIR,
    max_games: int | None = None,
    sleep_s: float = 0.0,
    progress_every: int = 100,
) -> pd.DataFrame:
    """
    Load MLB player boxscores for seasons by walking the schedule.

    Caches each game parquet under data/cache/mlb_boxscores by default.
    Use max_games for fast smokes.
    """
    season_list = as_season_list(seasons, [2023, 2024])
    sched = load_mlb_schedules(season_list)
    if not len(sched):
        raise MultiSportDataError(f"MLB schedule empty for seasons={season_list}")

    # Balance capped samples across seasons so walk-forward still has train/test years.
    if max_games is not None:
        cap = int(max_games)
        seasons_present = [
            int(s) for s in sched["season"].dropna().astype(int).unique().tolist()
        ]
        seasons_present.sort()
        per = max(1, cap // max(1, len(seasons_present)))
        parts: list[str] = []
        for s in seasons_present:
            ids = (
                sched.loc[sched["season"].astype(int) == s, "game_id"]
                .astype(str)
                .drop_duplicates()
                .tolist()
            )
            parts.extend(ids[:per])
        game_ids = parts[:cap]
    else:
        game_ids = sched["game_id"].astype(str).drop_duplicates().tolist()

    cdir = Path(cache_dir) if cache_dir is not None else None
    frames: list[pd.DataFrame] = []
    errors = 0
    for i, gid in enumerate(game_ids, start=1):
        try:
            box = load_mlb_boxscore_game(gid, cache_dir=cdir)
            if not len(box):
                continue
            # attach schedule context
            meta = sched.loc[sched["game_id"].astype(str) == str(gid)].head(1)
            if len(meta):
                box = box.copy()
                box["season"] = int(meta.iloc[0]["season"])
                box["gameday"] = meta.iloc[0]["gameday"]
                box["home_team"] = meta.iloc[0]["home_team"]
                box["away_team"] = meta.iloc[0]["away_team"]
            frames.append(box)
        except Exception:
            errors += 1
            continue
        if sleep_s > 0:
            time.sleep(sleep_s)
        if progress_every and i % progress_every == 0:
            print(f"mlb boxscores fetched {i}/{len(game_ids)} ok_frames={len(frames)} errors={errors}")

    if not frames:
        raise MultiSportDataError(
            f"no MLB boxscores loaded for seasons={season_list} games={len(game_ids)} errors={errors}"
        )
    out = pd.concat(frames, ignore_index=True)
    return out


def load_mlb_player_game_panel(
    seasons: int | Iterable[int] | None = None,
    *,
    positions: set[str] | None = None,
    min_pa: float = 1.0,
    cache_dir: str | Path | None = DEFAULT_CACHE_DIR,
    max_games: int | None = None,
) -> pd.DataFrame:
    """
    Build MLB batter player-game panel from boxscores.

    Default keeps rows with plate appearances / at-bats evidence (hitters).
    Pitchers with no batting line are dropped unless positions includes P and min_pa=0.
    """
    raw = load_mlb_player_boxscores(seasons, cache_dir=cache_dir, max_games=max_games)
    df = raw.copy()

    # batting counting stats (game-level)
    ab = pd.to_numeric(df.get("stats_batting_at_bats"), errors="coerce").fillna(0.0)
    hits = pd.to_numeric(df.get("stats_batting_hits"), errors="coerce").fillna(0.0)
    bb = pd.to_numeric(df.get("stats_batting_base_on_balls"), errors="coerce").fillna(0.0)
    hbp = pd.to_numeric(df.get("stats_batting_hit_by_pitch"), errors="coerce").fillna(0.0)
    sf = pd.to_numeric(df.get("stats_batting_sac_flies"), errors="coerce").fillna(0.0)
    hr = pd.to_numeric(df.get("stats_batting_home_runs"), errors="coerce").fillna(0.0)
    doubles = pd.to_numeric(df.get("stats_batting_doubles"), errors="coerce").fillna(0.0)
    triples = pd.to_numeric(df.get("stats_batting_triples"), errors="coerce").fillna(0.0)
    rbi = pd.to_numeric(df.get("stats_batting_rbi"), errors="coerce").fillna(0.0)
    runs = pd.to_numeric(df.get("stats_batting_runs"), errors="coerce").fillna(0.0)
    so = pd.to_numeric(df.get("stats_batting_strike_outs"), errors="coerce").fillna(0.0)
    sb = pd.to_numeric(df.get("stats_batting_stolen_bases"), errors="coerce").fillna(0.0)
    tb = pd.to_numeric(df.get("stats_batting_total_bases"), errors="coerce").fillna(0.0)
    pa = pd.to_numeric(df.get("stats_batting_plate_appearances"), errors="coerce")
    if pa is None or pa.isna().all():
        pa = ab + bb + hbp + sf
    else:
        pa = pa.fillna(ab + bb + hbp + sf)

    pos = df.get("position_abbreviation", pd.Series([""] * len(df))).astype(str)
    side = df.get("team_side", pd.Series([""] * len(df))).astype(str).str.lower()

    out = pd.DataFrame(
        {
            "game_id": df["game_id"].astype(str),
            "season": pd.to_numeric(df.get("season"), errors="coerce").astype("Int64"),
            "gameday": pd.to_datetime(df.get("gameday"), errors="coerce"),
            "player_id": df["person_id"].astype(str),
            "player_name": df.get("person_boxscore_name", df.get("person_full_name")).astype(str),
            "player_display_name": df.get("person_full_name", df.get("person_boxscore_name")).astype(str),
            "position": pos,
            "team": df.get("team_name").astype(str),
            "is_home": (side == "home").astype(int),
            "home_team": df.get("home_team"),
            "away_team": df.get("away_team"),
            "at_bats": ab,
            "hits": hits,
            "walks": bb,
            "hbp": hbp,
            "sac_flies": sf,
            "plate_appearances": pa,
            "home_runs": hr,
            "doubles": doubles,
            "triples": triples,
            "rbi": rbi,
            "runs": runs,
            "strikeouts": so,
            "stolen_bases": sb,
            "total_bases": tb,
        }
    )
    # opponent from home/away
    out["opponent"] = out.apply(
        lambda r: r["away_team"]
        if int(r["is_home"]) == 1
        else r["home_team"],
        axis=1,
    )
    out["week"] = out["gameday"].dt.isocalendar().week.astype("Int64")
    # singles for fantasy
    singles = (out["hits"] - out["doubles"] - out["triples"] - out["home_runs"]).clip(lower=0)
    # common draftkings-ish batter fantasy points proxy
    out["fantasy_points"] = (
        3.0 * singles
        + 5.0 * out["doubles"]
        + 8.0 * out["triples"]
        + 10.0 * out["home_runs"]
        + 2.0 * out["rbi"]
        + 2.0 * out["runs"]
        + 2.0 * out["walks"]
        + 2.0 * out["hbp"]
        + 5.0 * out["stolen_bases"]
    )

    if positions is not None:
        out = out[out["position"].isin(positions)].copy()
    out = out[out["plate_appearances"] >= float(min_pa)].copy()
    out = out.dropna(subset=["game_id", "season", "player_id"])
    out = out.sort_values(["player_id", "season", "week", "gameday", "game_id"]).reset_index(drop=True)
    return out
