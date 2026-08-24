"""Leakage audits for pre-game feature matrices."""

from __future__ import annotations

from typing import Any

import pandas as pd

from sports_ds.features.team_form import add_pregame_form_features


def audit_pregame_form_features(panel: pd.DataFrame) -> dict[str, Any]:
    """Check that pre-game form features only use prior games (shift-1).

    Returns a structured audit with status CLEAN / NOT_CLEAN.
    """
    required = ["team", "season", "week", "game_id", "won", "points_for", "points_against", "point_diff"]
    missing = [c for c in required if c not in panel.columns]
    if missing:
        return {"status": "NOT_CLEAN", "errors": [f"missing columns: {missing}"], "checks": []}

    featured = add_pregame_form_features(panel)
    checks: list[dict[str, Any]] = []
    errors: list[str] = []

    # Keep the same team timeline order used by add_pregame_form_features.
    sort_cols = [c for c in ["team", "season", "week", "gameday", "game_id"] if c in featured.columns]

    # first game for each team must have null expanding history
    first = (
        featured.sort_values(sort_cols)
        .groupby("team", as_index=False)
        .head(1)
    )
    bad_first = first["pre_games_played"].notna() & (first["pre_games_played"] != 0)
    # pre_games_played uses expanding count after shift; first row should be NA
    na_ok = first["pre_win_pct"].isna().all()
    checks.append(
        {
            "name": "first_game_history_null",
            "pass": bool(na_ok),
            "detail": "pre_win_pct is NA on each team's first game",
        }
    )
    if not na_ok:
        errors.append("first-game pre_win_pct not all NA")

    # reconstructed expanding mean after shift should match feature
    tmp = featured.sort_values(sort_cols).copy()
    recon = tmp.groupby("team", sort=False)["won"].transform(lambda s: s.shift(1).expanding().mean())
    comparable = tmp["pre_win_pct"].notna() & recon.notna()
    if comparable.any():
        max_abs = float((tmp.loc[comparable, "pre_win_pct"] - recon.loc[comparable]).abs().max())
        # float noise across sports panels; still tiny vs any real leakage
        ok = max_abs < 1e-6
    else:
        max_abs = float("nan")
        ok = False
        errors.append("no comparable rows for expanding recon")
    checks.append(
        {
            "name": "expanding_win_pct_matches_shift1",
            "pass": bool(ok),
            "max_abs_diff": max_abs,
        }
    )
    if not ok:
        errors.append("pre_win_pct does not match shift(1).expanding().mean()")

    # opponent join should not create self-team mismatch
    if "opp_pre_win_pct" in featured.columns:
        # for a game, team's opponent history should equal opponent's own pre_win_pct
        self_map = featured.set_index(["game_id", "team"])["pre_win_pct"]
        opp_lookup = featured.apply(
            lambda r: self_map.get((r["game_id"], r["opponent"])), axis=1
        )
        both = featured["opp_pre_win_pct"].notna() & opp_lookup.notna()
        if both.any():
            opp_max = float((featured.loc[both, "opp_pre_win_pct"] - opp_lookup.loc[both]).abs().max())
            opp_ok = opp_max < 1e-9
        else:
            opp_max = float("nan")
            opp_ok = True
        checks.append(
            {
                "name": "opponent_features_match_opponent_row",
                "pass": bool(opp_ok),
                "max_abs_diff": opp_max,
            }
        )
        if not opp_ok:
            errors.append("opp_pre_win_pct mismatch vs opponent row")

    # unused but keeps linter quiet if future checks want bad_first
    _ = bad_first

    status = "CLEAN" if not errors else "NOT_CLEAN"
    return {
        "status": status,
        "n_rows": int(len(featured)),
        "n_teams": int(featured["team"].nunique()),
        "checks": checks,
        "errors": errors,
    }
