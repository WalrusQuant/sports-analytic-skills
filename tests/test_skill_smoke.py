from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def run_helper(
    relative_script: str, *args: str, cwd: Path, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / relative_script), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=30,
        check=check,
    )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_eda_and_calibration_helpers_accept_user_artifacts(tmp_path: Path) -> None:
    panel = tmp_path / "team_games.csv"
    write_csv(
        panel,
        [
            {"season": 2024, "game_id": "g1", "team": "A", "is_home": 1, "won": 1},
            {"season": 2024, "game_id": "g1", "team": "B", "is_home": 0, "won": 0},
            {"season": 2024, "game_id": "g2", "team": "B", "is_home": 1, "won": 0},
            {"season": 2024, "game_id": "g2", "team": "A", "is_home": 0, "won": 1},
        ],
    )
    eda_out = tmp_path / "eda.json"
    run_helper(
        "skills/eda-sports/scripts/panel_report.py",
        "--input",
        str(panel),
        "--out",
        str(eda_out),
        cwd=tmp_path,
    )
    eda = json.loads(eda_out.read_text(encoding="utf-8"))
    assert eda["rows"] == 4
    assert eda["n_games"] == 2
    assert eda["duplicate_game_team_keys"] == 0

    predictions = tmp_path / "predictions.csv"
    write_csv(
        predictions,
        [
            {"season": 2023, "y_true": 0, "p_pred": 0.1},
            {"season": 2023, "y_true": 0, "p_pred": 0.3},
            {"season": 2023, "y_true": 1, "p_pred": 0.7},
            {"season": 2024, "y_true": 0, "p_pred": 0.2},
            {"season": 2024, "y_true": 1, "p_pred": 0.8},
            {"season": 2024, "y_true": 1, "p_pred": 0.9},
        ],
    )
    calibration_out = tmp_path / "calibration.json"
    run_helper(
        "skills/calibration-check/scripts/calibration_report.py",
        "--input",
        str(predictions),
        "--target",
        "y_true",
        "--probability",
        "p_pred",
        "--group-col",
        "season",
        "--out",
        str(calibration_out),
        cwd=tmp_path,
    )
    calibration = json.loads(calibration_out.read_text(encoding="utf-8"))
    assert calibration["n"] == 6
    assert set(calibration["groups"]) == {"2023", "2024"}
    assert 0 <= calibration["brier"] <= 1


def test_probability_simulation_and_results_report_handoff(tmp_path: Path) -> None:
    schedule = tmp_path / "schedule.csv"
    write_csv(
        schedule,
        [
            {
                "season": 2024,
                "game_id": "g1",
                "is_home": 1,
                "team": "A",
                "opponent": "B",
                "win_probability": 1.0,
            },
            {
                "season": 2024,
                "game_id": "g2",
                "is_home": 1,
                "team": "B",
                "opponent": "A",
                "win_probability": 0.0,
            },
        ],
    )
    simulation_out = tmp_path / "simulation.json"
    run_helper(
        "skills/simulation-sports/scripts/season_win_sim.py",
        "--input",
        str(schedule),
        "--season",
        "2024",
        "--n-sims",
        "100",
        "--threshold",
        "2",
        "--out",
        str(simulation_out),
        cwd=tmp_path,
    )
    simulation = json.loads(simulation_out.read_text(encoding="utf-8"))
    standings = {row["team"]: row for row in simulation["standings"]}
    assert standings["A"]["mean_wins"] == 2.0
    assert standings["A"]["prob_wins_at_least_threshold"] == 1.0
    assert standings["B"]["mean_wins"] == 0.0

    results = tmp_path / "results.json"
    results.write_text(
        json.dumps(
            {
                "title": "Simulation smoke",
                "question": "What is the win-total distribution?",
                "data": {"sport": "synthetic", "grain": "game", "period": "2024", "n": 2},
                "methods": {
                    "baseline": "zero wins",
                    "simulation": "Bernoulli season simulation",
                },
                "validation": {
                    "design": "deterministic boundary probabilities",
                    "primary_metric": "mean_wins",
                },
                "results": {"team_a_mean_wins": 2.0},
                "interpretation": "Boundary probabilities produce deterministic standings.",
                "limits": ["Synthetic test data."],
                "reproduction": {"simulation_artifact": str(simulation_out)},
            }
        ),
        encoding="utf-8",
    )
    report_out = tmp_path / "report.md"
    run_helper(
        "skills/results-reporting/scripts/render_results_report.py",
        "--json",
        str(results),
        "--out",
        str(report_out),
        cwd=tmp_path,
    )
    report = report_out.read_text(encoding="utf-8")
    assert "# Simulation smoke" in report
    assert "## Validation" in report
    assert "Synthetic test data." in report


def test_results_report_rejects_missing_evidence_contract(tmp_path: Path) -> None:
    valid = {
        "question": "Is this result adequately documented?",
        "data": {"grain": "game", "n": 20},
        "methods": {"baseline": "naive"},
        "validation": {"design": "holdout", "primary_metric": "score"},
        "results": {"score": 1.0},
        "limits": ["Synthetic."],
        "reproduction": {"artifact": "metrics.json"},
    }
    invalid_documents = [
        ({**valid, "data": {}}, "data must be a non-empty JSON object"),
        ({**valid, "data": {"grain": "game"}}, "data missing required fields: n"),
        ({**valid, "methods": {"analysis": "simulation"}}, "methods missing required fields: baseline"),
        (
            {**valid, "validation": {"design": "holdout"}},
            "validation missing required fields: primary_metric",
        ),
        ({**valid, "results": {}}, "results must be a non-empty JSON object"),
        ({**valid, "limits": []}, "limits must be a non-empty array of strings"),
        ({**valid, "reproduction": {}}, "reproduction must be a non-empty JSON object"),
    ]
    for index, (document, expected_error) in enumerate(invalid_documents):
        results = tmp_path / f"incomplete-{index}.json"
        results.write_text(json.dumps(document), encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "skills/results-reporting/scripts/render_results_report.py"),
                "--json",
                str(results),
                "--out",
                str(tmp_path / f"report-{index}.md"),
            ],
            cwd=tmp_path,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        assert completed.returncode != 0
        assert expected_error in completed.stderr


def test_leakage_first_event_finding_requires_review(tmp_path: Path) -> None:
    panel = tmp_path / "pregame.csv"
    write_csv(
        panel,
        [
            {"team": "A", "event_time": 1, "won": 0, "pre_rate": 0.4},
            {"team": "B", "event_time": 1, "won": 1, "pre_rate": 0.6},
            {"team": "A", "event_time": 2, "won": 1, "pre_rate": 0.5},
            {"team": "B", "event_time": 2, "won": 0, "pre_rate": 0.5},
        ],
    )
    out = tmp_path / "leakage.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "skills/leakage-audit/scripts/audit_pregame_features.py"),
            "--input",
            str(panel),
            "--target",
            "won",
            "--features",
            "pre_rate",
            "--entity-col",
            "team",
            "--time-col",
            "event_time",
            "--out",
            str(out),
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert completed.returncode == 1
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["verdict"] == "REVIEW REQUIRED"
    first_event = next(item for item in report["findings"] if item["id"] == "first_event_history_review")
    assert first_event["status"] == "REVIEW"


def test_empty_inputs_do_not_receive_false_clean_verdicts(tmp_path: Path) -> None:
    empty = tmp_path / "empty.csv"
    empty.write_text("team,event_time,feature,won\n", encoding="utf-8")

    commands = [
        (
            "skills/leakage-audit/scripts/audit_pregame_features.py",
            "--input",
            str(empty),
            "--target",
            "won",
            "--features",
            "feature",
            "--entity-col",
            "team",
            "--time-col",
            "event_time",
        ),
        (
            "skills/predictive-modeling/scripts/leakage_smoke.py",
            "--input",
            str(empty),
            "--target",
            "won",
            "--features",
            "feature",
        ),
    ]
    for relative_script, *args in commands:
        result = run_helper(relative_script, *args, cwd=tmp_path, check=False)
        assert result.returncode != 0
        assert "no rows" in (result.stdout + result.stderr).lower()
        assert "clean" not in result.stdout.lower()


def test_ewma_rejects_same_time_events_without_strict_sequence(tmp_path: Path) -> None:
    events = tmp_path / "events.csv"
    write_csv(
        events,
        [
            {"team": "A", "event_time": "2024-01-01", "sequence": 1, "margin": 3},
            {"team": "A", "event_time": "2024-01-01", "sequence": 2, "margin": -1},
            {"team": "A", "event_time": "2024-01-02", "sequence": 3, "margin": 2},
        ],
    )

    ambiguous = run_helper(
        "skills/time-series-sports/scripts/ewma_form.py",
        "--input",
        str(events),
        "--entity-col",
        "team",
        "--time-col",
        "event_time",
        "--values",
        "margin",
        "--out",
        str(tmp_path / "ambiguous.csv"),
        cwd=tmp_path,
        check=False,
    )
    assert ambiguous.returncode != 0
    assert "ambiguous event order" in (ambiguous.stdout + ambiguous.stderr).lower()

    ordered_out = tmp_path / "ordered.csv"
    run_helper(
        "skills/time-series-sports/scripts/ewma_form.py",
        "--input",
        str(events),
        "--entity-col",
        "team",
        "--time-col",
        "event_time",
        "--order-col",
        "sequence",
        "--values",
        "margin",
        "--out",
        str(ordered_out),
        cwd=tmp_path,
    )
    assert ordered_out.is_file()


def test_elo_rejects_same_time_appearances_for_one_team(tmp_path: Path) -> None:
    games = tmp_path / "games.csv"
    write_csv(
        games,
        [
            {
                "season": 2024,
                "game_date": "2024-01-01T12:00:00Z",
                "game_id": "g1",
                "home_team": "A",
                "away_team": "B",
                "home_score": 3,
                "away_score": 1,
            },
            {
                "season": 2024,
                "game_date": "2024-01-01T12:00:00Z",
                "game_id": "g2",
                "home_team": "C",
                "away_team": "A",
                "home_score": 2,
                "away_score": 1,
            },
        ],
    )
    result = run_helper(
        "skills/ratings-strength-models/scripts/elo_asof.py",
        "--input",
        str(games),
        "--out",
        str(tmp_path / "elo.csv"),
        cwd=tmp_path,
        check=False,
    )
    assert result.returncode != 0
    assert "does not strictly order every team's games" in (
        result.stdout + result.stderr
    ).lower()


def test_model_card_stub_has_clean_markdown_structure(tmp_path: Path) -> None:
    output = tmp_path / "model-card.md"
    run_helper(
        "skills/model-card/scripts/write_card_stub.py",
        "--name",
        "home-form-logit",
        "--version",
        "v1",
        "--grain",
        "team-game",
        "--out",
        str(output),
        cwd=tmp_path,
    )
    card = output.read_text(encoding="utf-8")
    assert card.startswith("# Model card: home-form-logit (v1)\n")
    assert "## Data\n\n- Sources:" in card
    assert "- Sample size:\n" in card
    assert "## Reproduction\n\n```bash\n" in card
    assert "  ```" not in card


def test_model_artifacts_flow_to_calibration_and_visualization(tmp_path: Path) -> None:
    modeling_table = tmp_path / "modeling.csv"
    rows = []
    for season in range(2020, 2025):
        for game in range(8):
            signal = 1 if game % 2 == 0 else -1
            rows.append(
                {
                    "row_id": f"{season}-{game}",
                    "season": season,
                    "won": int(signal > 0),
                    "rating_diff": signal + (season - 2020) * 0.02,
                }
            )
    write_csv(modeling_table, rows)

    folds = tmp_path / "folds.json"
    predictions = tmp_path / "predictions.csv"
    run_helper(
        "skills/predictive-modeling/scripts/run_fold_table.py",
        "--input",
        str(modeling_table),
        "--target",
        "won",
        "--features",
        "rating_diff",
        "--split-col",
        "season",
        "--id-cols",
        "row_id",
        "--min-train-groups",
        "2",
        "--out",
        str(folds),
        "--predictions-out",
        str(predictions),
        cwd=tmp_path,
    )
    artifact = json.loads(folds.read_text(encoding="utf-8"))
    assert artifact["validation"]["design"] == "expanding_window"
    assert len(artifact["folds"]) == 3
    assert "logistic_log_loss" in artifact["folds"][0]

    with predictions.open(newline="", encoding="utf-8") as handle:
        prediction_rows = list(csv.DictReader(handle))
    assert len(prediction_rows) == 24
    assert {
        "row_id",
        "fold",
        "y_true",
        "constant_probability",
        "logistic_probability",
        "hist_gbm_probability",
    } <= set(prediction_rows[0])

    calibration = tmp_path / "model-calibration.json"
    run_helper(
        "skills/calibration-check/scripts/calibration_report.py",
        "--input",
        str(predictions),
        "--target",
        "y_true",
        "--probability",
        "logistic_probability",
        "--group-col",
        "fold",
        "--out",
        str(calibration),
        cwd=tmp_path,
    )
    assert json.loads(calibration.read_text(encoding="utf-8"))["n"] == 24

    chart = tmp_path / "walk-forward.png"
    run_helper(
        "skills/sports-visualization/scripts/plot_walkforward_metrics.py",
        "--json",
        str(folds),
        "--metric",
        "logistic_log_loss",
        "--baseline",
        "constant_log_loss",
        "--out",
        str(chart),
        cwd=tmp_path,
    )
    assert chart.stat().st_size > 0
