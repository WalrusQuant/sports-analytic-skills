from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_script(relative_path: str, module_name: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_nfl_schedule_transform_and_panel_summary_are_offline() -> None:
    pl = pytest.importorskip("polars")
    builder = load_script(
        "skills/nflreadpy/scripts/load_game_panel.py", "standalone_nfl_builder"
    )
    describer = load_script(
        "skills/nflreadpy/scripts/describe_panel.py", "standalone_nfl_describer"
    )
    schedule = pl.DataFrame(
        {
            "game_id": ["g1", "g2", "future"],
            "season": [2024, 2024, 2024],
            "week": [1, 2, 3],
            "gameday": ["2024-09-01", "2024-09-08", "2024-09-15"],
            "home_team": ["A", "B", "A"],
            "away_team": ["B", "A", "B"],
            # Strings exercise numeric casting before outcome comparisons.
            "home_score": ["9", "17", None],
            "away_score": ["10", "17", None],
        }
    )

    panel = builder.build_panel(schedule)
    summary = describer.summarize_panel(panel)

    assert panel.height == 4
    assert panel["game_id"].n_unique() == 2
    assert summary["two_rows_per_game"] is True
    assert summary["complementary_rows"] is True
    assert summary["valid_row_logic"] is True
    home_g1 = panel.filter((pl.col("game_id") == "g1") & (pl.col("is_home") == 1))
    assert home_g1["won"].item() == 0
    assert home_g1["point_diff"].item() == -1.0
    assert panel.filter(pl.col("game_id") == "g2")["tied"].to_list() == [1, 1]

    broken = panel.with_columns(
        pl.when((pl.col("game_id") == "g1") & (pl.col("is_home") == 0))
        .then(None)
        .otherwise(pl.col("is_home"))
        .alias("is_home")
    )
    broken_summary = describer.summarize_panel(broken)
    assert broken_summary["complementary_rows"] is False
    assert broken_summary["valid_row_logic"] is False


def test_standalone_elo_toy_is_asof_and_probability_symmetric() -> None:
    elo = load_script(
        "skills/ratings-strength-models/scripts/elo_asof.py", "standalone_elo_builder"
    )
    games = pd.DataFrame(
        [
            {
                "season": 2024,
                "game_date": "2024-01-01",
                "game_id": "g1",
                "home_team": "A",
                "away_team": "B",
                "home_score": 20,
                "away_score": 10,
            },
            {
                "season": 2024,
                "game_date": "2024-01-02",
                "game_id": "g2",
                "home_team": "B",
                "away_team": "A",
                "home_score": 7,
                "away_score": 14,
            },
        ]
    )

    output = elo.build_elo_table(games, k=20, home_adv=65, init=1500)

    assert len(output) == 4
    for _, game in output.groupby("game_id"):
        assert game["win_probability"].sum() == pytest.approx(1.0)
        assert game["elo_diff"].sum() == pytest.approx(0.0)
    first_home = output[(output["game_id"] == "g1") & (output["is_home"] == 1)].iloc[0]
    assert first_home["elo_pre"] == 1500
    assert first_home["elo_diff"] == 65
    second_a = output[(output["game_id"] == "g2") & (output["team"] == "A")].iloc[0]
    assert second_a["elo_pre"] > 1500


def test_standalone_exporters_refuse_existing_or_input_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    elo = load_script(
        "skills/ratings-strength-models/scripts/elo_asof.py", "standalone_elo_io"
    )
    games = pd.DataFrame(
        [
            {
                "season": 2024,
                "game_date": "2024-01-01",
                "game_id": "g1",
                "home_team": "A",
                "away_team": "B",
                "home_score": 20,
                "away_score": 10,
            }
        ]
    )
    source = tmp_path / "games.csv"
    games.to_csv(source, index=False)
    original = source.read_bytes()
    monkeypatch.setattr(sys, "argv", ["elo_asof.py", "--input", str(source), "--out", str(source)])
    with pytest.raises(SystemExit) as same_file:
        elo.main()
    assert same_file.value.code == 2
    assert source.read_bytes() == original

    existing = tmp_path / "elo.csv"
    existing.write_text("sentinel\n", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        ["elo_asof.py", "--input", str(source), "--out", str(existing)],
    )
    with pytest.raises(SystemExit) as existing_file:
        elo.main()
    assert existing_file.value.code == 2
    assert existing.read_text(encoding="utf-8") == "sentinel\n"

    nfl = load_script(
        "skills/nflreadpy/scripts/load_game_panel.py", "standalone_nfl_io"
    )
    parquet = tmp_path / "panel.parquet"
    parquet.write_bytes(b"sentinel")
    monkeypatch.setattr(
        sys,
        "argv",
        ["load_game_panel.py", "--seasons", "2024", "--out", str(parquet)],
    )
    with pytest.raises(SystemExit) as protected_parquet:
        nfl.main()
    assert protected_parquet.value.code == 2
    assert parquet.read_bytes() == b"sentinel"
