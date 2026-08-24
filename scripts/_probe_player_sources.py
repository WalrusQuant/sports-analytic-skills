#!/usr/bin/env python3
"""Probe NBA/MLB player-level loaders."""
from __future__ import annotations
import traceback

def _to_df(obj):
    if hasattr(obj, "to_pandas"):
        return obj.to_pandas()
    return obj

def try_call(label, fn, *args, **kwargs):
    print(f"== {label} ==")
    try:
        out = fn(*args, **kwargs)
        df = _to_df(out)
        print(" type", type(out))
        if hasattr(df, "columns"):
            print(" rows", len(df), "cols", list(df.columns)[:50])
            if len(df):
                rec = df.iloc[0].to_dict()
                print(" sample", {k: rec[k] for k in list(rec)[:18]})
        else:
            print(" out", str(out)[:300])
    except Exception as exc:
        print(" FAIL", type(exc).__name__, exc)
        traceback.print_exc(limit=2)
    print()

def main():
    from sportsdataverse.nba import (
        load_nba_player_boxscore,
        load_nba_stats_player_boxscores,
        load_nba_stats_player_game_logs,
    )
    for label, fn, args in [
        ("load_nba_player_boxscore([2024])", load_nba_player_boxscore, ([2024],)),
        ("load_nba_stats_player_boxscores([2024])", load_nba_stats_player_boxscores, ([2024],)),
        ("load_nba_stats_player_game_logs([2024])", load_nba_stats_player_game_logs, ([2024],)),
    ]:
        try_call(label, fn, *args)

    try:
        from sportsdataverse import mlb
        from sports_ds.data.mlb import load_mlb_schedules
        print("mlb_person_game_stats exists", hasattr(mlb, "mlb_person_game_stats"))
        print("mlb_boxscore exists", hasattr(mlb, "mlb_boxscore"))
        sched = load_mlb_schedules([2024])
        print("mlb schedule rows", len(sched))
        gpk = int(float(sched.iloc[10]["game_id"]))
        print("sample game_pk", gpk)
        if hasattr(mlb, "mlb_boxscore"):
            try_call("mlb_boxscore", mlb.mlb_boxscore, gpk)
        if hasattr(mlb, "mlb_person_game_stats"):
            try_call("mlb_person_game_stats", mlb.mlb_person_game_stats, personId=660271, season=2024)
    except Exception as exc:
        print("mlb block fail", type(exc).__name__, exc)
        traceback.print_exc(limit=3)

    try:
        from pybaseball import batting_stats, pitching_stats
        try_call("batting_stats(2024)", batting_stats, 2024, qual=50)
        try_call("pitching_stats(2024)", pitching_stats, 2024, qual=20)
    except Exception as exc:
        print("pybaseball fail", exc)

if __name__ == "__main__":
    main()
