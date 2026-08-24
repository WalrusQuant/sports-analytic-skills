#!/usr/bin/env python3
"""Verify sports_ds import, core modules, and a tiny NFL panel load."""

from __future__ import annotations


def main() -> int:
    import sports_ds
    from sports_ds.audit.leakage import audit_pregame_form_features
    from sports_ds.data.nfl import load_team_game_panel
    from sports_ds.features.registry import list_feature_specs
    from sports_ds.metrics.calibration import expected_calibration_error
    from sports_ds.ratings.elo import build_elo_asof_table

    panel = load_team_game_panel([2024])
    elo = build_elo_asof_table(panel.head(200) if len(panel) > 200 else panel)
    audit = audit_pregame_form_features(panel.head(400) if len(panel) > 400 else panel)
    specs = list_feature_specs()
    _ = expected_calibration_error([0, 1, 1, 0], [0.1, 0.9, 0.8, 0.2], n_bins=4)

    print(f"sports_ds={getattr(sports_ds, '__version__', 'unknown')}")
    print(f"panel_rows={len(panel)} teams={panel['team'].nunique()} cols={len(panel.columns)}")
    print(f"elo_rows={len(elo)} audit={audit.get('status')} feature_specs={len(specs)}")
    print("OK")
    return 0 if audit.get("status") == "CLEAN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
