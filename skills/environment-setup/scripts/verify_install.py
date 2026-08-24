#!/usr/bin/env python3
"""Verify sports_ds import and a tiny NFL panel load."""

from __future__ import annotations


def main() -> int:
    import sports_ds
    from sports_ds.data.nfl import load_team_game_panel

    panel = load_team_game_panel([2024])
    print(f"sports_ds={getattr(sports_ds, '__version__', 'unknown')}")
    print(f"panel_rows={len(panel)} teams={panel['team'].nunique()} cols={len(panel.columns)}")
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
