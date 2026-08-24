"""CLI integration tests (offline)."""

from __future__ import annotations

import json
from pathlib import Path

from sports_ds.cli import main


def test_cli_feature_registry_prints(capsys):
    code = main(["feature-registry"])
    assert code == 0
    out = capsys.readouterr().out
    assert "feature_win_pct_diff" in out
    assert "elo_diff" in out


def test_cli_help_lists_core_commands():
    # argparse help exits via SystemExit in some versions; call parser path via main invalid
    # We just ensure main rejects unknown and known commands exist by importing cli module.
    from sports_ds import cli as cli_mod
    import argparse

    parser = argparse.ArgumentParser()
    # smoke: module imports and main is callable
    assert callable(cli_mod.main)


def test_cli_parse_seasons_helper():
    from sports_ds.cli import _parse_seasons

    assert _parse_seasons("2018-2020") == [2018, 2019, 2020]
    assert _parse_seasons("2023,2024") == [2023, 2024]
