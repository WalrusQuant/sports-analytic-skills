"""MLB player-game loading via sportsdataverse per-game boxscores (cached)."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable

import pandas as pd

from sports_ds.data.mlb import load_mlb_schedules
from sports_ds.data.panel import as_season_list, assign_season_week, to_pandas
from sports_ds.data.sdv_common import MultiSportDataError, require_sportsdataverse


DEFAULT_CACHE_DIR = Path("data/cache/mlb_boxscores")
DEFAULT_PANEL_CACHE_DIR = Path("data/cache/mlb_player_panels")


def _boxscore_path(cache_dir: Path, game_pk: str) -> Path:
    return cache_dir / f"{game_pk}.parquet"


def _panel_cache_path(panel_cache_dir: Path, seasons: list[int], max_games: int | None) -> Path:
    tag = "-".join(str(s) for s in seasons)
    mg = "all" if max_games is None else f"g{int(max_games)}"
    return panel_cache_dir / f"batters_{tag}_{mg}.parquet"


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


def _fetch_one(gid: str, sched: pd.DataFrame, cdir: Path | None) -> pd.DataFrame | None:
    try:
        box = load_mlb_boxscore_game(gid, cache_dir=cdir)
        if not len(box):
            return None
        meta = sched.loc[sched["game_id"].astype(str) == str(gid)].head(1)
        if len(meta):
            box = box.copy()
            box["season"] = int(meta.iloc[0]["season"])
            box["gameday"] = meta.iloc[0]["gameday"]
            box["home_team"] = meta.iloc[0]["home_team"]
            box["away_team"] = meta.iloc[0]["away_team"]
        return box
    except Exception:
        return None


def load_mlb_player_boxscores(
    seasons: int | Iterable[int] | None = None,
    *,
    cache_dir: str | Path | None = DEFAULT_CACHE_DIR,
    max_games: int | None = None,
    sleep_s: float = 0.0,
    progress_every: int = 100,
    workers: int = 8,
) -> pd.DataFrame:
    """
    Load MLB player boxscores for seasons by walking the schedule.

    Caches each game parquet under data/cache/mlb_boxscores by default.
    Uses a thread pool for uncached games. Use max_games for fast smokes.
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
    if cdir is not None:
        cdir.mkdir(parents=True, exist_ok=True)

    # Split cached vs uncached for progress clarity
    cached_ids: list[str] = []
    fetch_ids: list[str] = []
    for gid in game_ids:
        if cdir is not None and _boxscore_path(cdir, gid).exists():
            cached_ids.append(gid)
        else:
            fetch_ids.append(gid)

    frames: list[pd.DataFrame] = []
    errors = 0

    # Load cached serially (fast local IO)
    for i, gid in enumerate(cached_ids, start=1):
        box = _fetch_one(gid, sched, cdir)
        if box is None:
            errors += 1
            continue
        frames.append(box)
        if progress_every and i % progress_every == 0:
            print(f"mlb boxscores cache-read {i}/{len(cached_ids)}")

    # Fetch missing in parallel
    if fetch_ids:
        workers = max(1, int(workers))
        done = 0
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(_fetch_one, gid, sched, cdir): gid for gid in fetch_ids}
            for fut in as_completed(futs):
                done += 1
                box = fut.result()
                if box is None:
                    errors += 1
                else:
                    frames.append(box)
                if sleep_s > 0:
                    time.sleep(sleep_s)
                if progress_every and done % progress_every == 0:
                    print(
                        f"mlb boxscores fetched {done}/{len(fetch_ids)} "
                        f"ok_frames={len(frames)} errors={errors}"
                    )

    if not frames:
        raise MultiSportDataError(
            f"no MLB boxscores loaded for seasons={season_list} games={len(game_ids)} errors={errors}"
        )
    out = pd.concat(frames, ignore_index=True)
    print(
        f"mlb boxscores total_games={len(game_ids)} rows={len(out)} "
        f"cached={len(cached_ids)} fetched={len(fetch_ids)} errors={errors}"
    )
    return out


def _starter_pitching_lines(raw: pd.DataFrame) -> pd.DataFrame:
    """One row per game/side for the starting pitcher, with this-game K and IP."""
    empty = pd.DataFrame(
        columns=["game_id", "team_side", "pitcher_id", "gameday", "season", "strikeouts", "innings"]
    )
    if "stats_pitching_games_started" not in raw.columns:
        return empty
    pid_col = "person_id" if "person_id" in raw.columns else None
    if pid_col is None:
        return empty
    gs = pd.to_numeric(raw.get("stats_pitching_games_started"), errors="coerce").fillna(0)
    starters = raw.loc[gs >= 1].copy()
    if not len(starters):
        return empty
    ip = pd.to_numeric(starters.get("stats_pitching_innings_pitched"), errors="coerce").fillna(0.0)
    k = pd.to_numeric(starters.get("stats_pitching_strike_outs"), errors="coerce").fillna(0.0)
    side = starters.get("team_side", pd.Series("", index=starters.index)).astype(str).str.lower()
    gameday = (
        pd.to_datetime(starters["gameday"], errors="coerce")
        if "gameday" in starters.columns
        else pd.Series(pd.NaT, index=starters.index)
    )
    season = (
        pd.to_numeric(starters["season"], errors="coerce")
        if "season" in starters.columns
        else pd.Series(pd.NA, index=starters.index)
    )
    out = pd.DataFrame(
        {
            "game_id": starters["game_id"].astype(str).to_numpy(),
            "team_side": side.to_numpy(),
            "pitcher_id": starters[pid_col].astype(str).to_numpy(),
            "gameday": gameday.to_numpy(),
            "season": season.to_numpy(),
            "strikeouts": k.to_numpy(),
            "innings": ip.astype(float).to_numpy(),
        }
    )
    return out.drop_duplicates(subset=["game_id", "team_side", "pitcher_id"], keep="first")


def _prior_starter_k9(starters: pd.DataFrame) -> pd.DataFrame:
    """Pitcher shift-1 expanding K/9. First start for a pitcher is NA (no prior)."""
    if starters is None or not len(starters):
        return pd.DataFrame(columns=["game_id", "team_side", "opp_k9", "opp_ip"])
    sort_cols = [c for c in ["pitcher_id", "gameday", "game_id"] if c in starters.columns]
    s = starters.sort_values(sort_cols).copy()
    g = s.groupby("pitcher_id", group_keys=False)
    s["pre_k"] = g["strikeouts"].apply(lambda series: series.shift(1).expanding().sum())
    s["pre_ip"] = g["innings"].apply(lambda series: series.shift(1).expanding().sum())
    s["opp_k9"] = (s["pre_k"] * 9.0) / s["pre_ip"].where(s["pre_ip"] > 0)
    s["opp_ip"] = s["pre_ip"]
    return s[["game_id", "team_side", "opp_k9", "opp_ip"]]


def _extract_opp_starter_k9(raw: pd.DataFrame) -> pd.DataFrame:
    """Opposing starter quality from *prior* starts, never this game's boxscore K/9."""
    return _prior_starter_k9(_starter_pitching_lines(raw))


def load_mlb_player_game_panel(
    seasons: int | Iterable[int] | None = None,
    *,
    positions: set[str] | None = None,
    min_pa: float = 1.0,
    cache_dir: str | Path | None = DEFAULT_CACHE_DIR,
    panel_cache_dir: str | Path | None = DEFAULT_PANEL_CACHE_DIR,
    max_games: int | None = None,
    workers: int = 8,
    use_panel_cache: bool = True,
    lineup_only: bool = True,
) -> pd.DataFrame:
    """
    Build MLB batter player-game panel from boxscores.

    Default keeps rows with plate appearances / at-bats evidence (hitters).
    When lineup_only=True, prefers batting_order present (starting lineup / PH with order).
    """
    season_list = as_season_list(seasons, [2023, 2024])
    pdir = Path(panel_cache_dir) if panel_cache_dir is not None else None
    if use_panel_cache and pdir is not None and max_games is None:
        pdir.mkdir(parents=True, exist_ok=True)
        ppath = _panel_cache_path(pdir, season_list, max_games)
        if ppath.exists():
            out = pd.read_parquet(ppath)
            if positions is not None:
                out = out[out["position"].isin(positions)].copy()
            out = out[out["plate_appearances"] >= float(min_pa)].copy()
            return out.reset_index(drop=True)

    raw = load_mlb_player_boxscores(
        seasons, cache_dir=cache_dir, max_games=max_games, workers=workers
    )
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
    if pa is None or getattr(pa, "isna", lambda: True)().all():
        pa = ab + bb + hbp + sf
    else:
        pa = pa.fillna(ab + bb + hbp + sf)

    pos = df.get("position_abbreviation", pd.Series([""] * len(df))).astype(str)
    side = df.get("team_side", pd.Series([""] * len(df))).astype(str).str.lower()
    batting_order = pd.to_numeric(df.get("batting_order"), errors="coerce")

    out = pd.DataFrame(
        {
            "game_id": df["game_id"].astype(str),
            "season": pd.to_numeric(df.get("season"), errors="coerce").astype("Int64"),
            "gameday": pd.to_datetime(df.get("gameday"), errors="coerce"),
            "player_id": df["person_id"].astype(str),
            "player_name": df.get("person_boxscore_name", df.get("person_full_name")).astype(str),
            "player_display_name": df.get("person_full_name", df.get("person_boxscore_name")).astype(
                str
            ),
            "position": pos,
            "team": df.get("team_name").astype(str),
            "is_home": (side == "home").astype(int),
            "home_team": df.get("home_team"),
            "away_team": df.get("away_team"),
            "batting_order": batting_order,
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
        lambda r: r["away_team"] if int(r["is_home"]) == 1 else r["home_team"],
        axis=1,
    )
    out = assign_season_week(out)

    # rates (game-level; form will shift/expand these)
    out["avg"] = out["hits"] / out["at_bats"].replace(0, pd.NA)
    out["obp"] = (out["hits"] + out["walks"] + out["hbp"]) / (
        out["at_bats"] + out["walks"] + out["hbp"] + out["sac_flies"]
    ).replace(0, pd.NA)
    out["slg"] = out["total_bases"] / out["at_bats"].replace(0, pd.NA)
    out["ops"] = out["obp"].fillna(0) + out["slg"].fillna(0)
    out["k_rate"] = out["strikeouts"] / out["plate_appearances"].replace(0, pd.NA)
    out["bb_rate"] = out["walks"] / out["plate_appearances"].replace(0, pd.NA)
    out["iso"] = out["slg"].fillna(0) - out["avg"].fillna(0)

    # singles for fantasy
    singles = (out["hits"] - out["doubles"] - out["triples"] - out["home_runs"]).clip(lower=0)
    out["singles"] = singles
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

    # opposing starter prior-start K/9; merge pitcher side opposite batter side
    starters = _extract_opp_starter_k9(df)
    if len(starters):
        away_st = starters[starters["team_side"] == "away"][["game_id", "opp_k9", "opp_ip"]]
        home_st = starters[starters["team_side"] == "home"][["game_id", "opp_k9", "opp_ip"]]
        home_bat = out[out["is_home"] == 1].merge(away_st, on="game_id", how="left")
        away_bat = out[out["is_home"] == 0].merge(home_st, on="game_id", how="left")
        out = pd.concat([home_bat, away_bat], ignore_index=True)
    else:
        out["opp_k9"] = pd.NA
        out["opp_ip"] = pd.NA

    if lineup_only:
        # keep starting lineup slots + anyone with PA and a batting order code
        # MLB API often encodes order like 100,200,... or 1-9
        bo = pd.to_numeric(out["batting_order"], errors="coerce")
        out = out[bo.notna() | (out["plate_appearances"] >= 2)].copy()

    if positions is not None:
        out = out[out["position"].isin(positions)].copy()
    out = out[out["plate_appearances"] >= float(min_pa)].copy()
    out = out.dropna(subset=["game_id", "season", "player_id"])
    out = out.sort_values(["player_id", "season", "week", "gameday", "game_id"]).reset_index(drop=True)

    # rest days
    g = out.groupby("player_id", group_keys=False)
    prev = g["gameday"].shift(1)
    out["rest_days"] = (pd.to_datetime(out["gameday"]) - pd.to_datetime(prev)).dt.days
    out.loc[out["rest_days"].notna(), "rest_days"] = out.loc[
        out["rest_days"].notna(), "rest_days"
    ].clip(lower=0, upper=15)

    if use_panel_cache and pdir is not None and max_games is None:
        ppath = _panel_cache_path(pdir, season_list, max_games)
        # cache unfiltered-by-position full hitter panel before position filter?
        # We already applied positions; cache the current out for this call signature.
        out.to_parquet(ppath, index=False)

    return out
