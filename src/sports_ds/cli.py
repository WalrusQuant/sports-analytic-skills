"""CLI for sports-ds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sports-ds", description="Sports data science toolkit")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_nfl = sub.add_parser("nfl-win-pipeline", help="Run NFL team-win walk-forward pipeline")
    p_nfl.add_argument("--seasons", default="2018-2024", help="e.g. 2018-2024 or 2020,2021,2022")
    p_nfl.add_argument("--min-train-seasons", type=int, default=2)
    p_nfl.add_argument("--json-out", default="", help="optional path to write full JSON result")

    p_margin = sub.add_parser("nfl-margin-pipeline", help="Run NFL team-margin walk-forward pipeline")
    p_margin.add_argument("--seasons", default="2018-2024")
    p_margin.add_argument("--min-train-seasons", type=int, default=2)
    p_margin.add_argument("--json-out", default="")

    p_elo = sub.add_parser("nfl-elo", help="Run NFL Elo as-of baseline walk-forward pipeline")
    p_elo.add_argument("--seasons", default="2018-2024")
    p_elo.add_argument("--min-train-seasons", type=int, default=2)
    p_elo.add_argument("--k", type=float, default=20.0)
    p_elo.add_argument("--home-adv", type=float, default=65.0)
    p_elo.add_argument("--json-out", default="")

    p_cal = sub.add_parser("calibrate", help="Walk-forward calibration report for win logistic")
    p_cal.add_argument("--seasons", default="2018-2024")
    p_cal.add_argument("--min-train-seasons", type=int, default=2)
    p_cal.add_argument("--bins", type=int, default=10)
    p_cal.add_argument("--json-out", default="")

    p_leak = sub.add_parser("leakage-audit", help="Audit pre-game form feature time-safety")
    p_leak.add_argument("--seasons", default="2023-2024")
    p_leak.add_argument("--json-out", default="")

    p_eda = sub.add_parser("nfl-eda", help="Load NFL team-game panel and print EDA summary")
    p_eda.add_argument("--seasons", default="2023-2024")

    p_nba_eda = sub.add_parser("nba-eda", help="Load NBA team-game panel and print EDA summary")
    p_nba_eda.add_argument("--seasons", default="2023-2024")

    p_nba = sub.add_parser("nba-win-pipeline", help="Run NBA team-win walk-forward pipeline")
    p_nba.add_argument("--seasons", default="2023-2024")
    p_nba.add_argument("--min-train-seasons", type=int, default=1)
    p_nba.add_argument("--json-out", default="")

    args = parser.parse_args(argv)

    if args.cmd == "nfl-win-pipeline":
        from sports_ds.pipelines.nfl_win_model import format_pipeline_report, run_nfl_win_pipeline

        seasons = _parse_seasons(args.seasons)
        result = run_nfl_win_pipeline(seasons=seasons, min_train_seasons=args.min_train_seasons)
        print(format_pipeline_report(result))
        _maybe_json(args.json_out, result, drop_keys=("eda",))
        return 0

    if args.cmd == "nfl-margin-pipeline":
        from sports_ds.pipelines.nfl_margin_model import format_margin_report, run_nfl_margin_pipeline

        seasons = _parse_seasons(args.seasons)
        result = run_nfl_margin_pipeline(seasons=seasons, min_train_seasons=args.min_train_seasons)
        print(format_margin_report(result))
        _maybe_json(args.json_out, result)
        return 0

    if args.cmd == "nfl-elo":
        from sports_ds.pipelines.nfl_elo_baseline import format_elo_report, run_nfl_elo_baseline

        seasons = _parse_seasons(args.seasons)
        result = run_nfl_elo_baseline(
            seasons=seasons,
            min_train_seasons=args.min_train_seasons,
            k=args.k,
            home_adv=args.home_adv,
        )
        print(format_elo_report(result))
        _maybe_json(args.json_out, result)
        return 0

    if args.cmd == "calibrate":
        from sports_ds.data.nfl import load_team_game_panel
        from sports_ds.features.team_form import add_pregame_form_features
        from sports_ds.metrics.calibration import (
            calibration_table,
            expected_calibration_error,
            verdict_from_ece,
        )
        from sports_ds.metrics.classification import brier_score, log_loss_binary
        from sports_ds.models.baselines import fit_logistic_baseline
        from sports_ds.pipelines.nfl_win_model import FEATURE_COLS
        from sports_ds.validation.splits import season_walk_forward_masks
        import numpy as np

        seasons = _parse_seasons(args.seasons)
        df = add_pregame_form_features(load_team_game_panel(seasons))
        df = df.dropna(subset=FEATURE_COLS + ["won"])
        df = df[(df.pre_games_played >= 3) & (df.opp_pre_games_played >= 3)].copy()
        ys, ps, per_season = [], [], []
        for season, tr, te in season_walk_forward_masks(df, min_train_seasons=args.min_train_seasons):
            _, res, pred = fit_logistic_baseline(df, FEATURE_COLS, tr, te)
            test = df.loc[te].dropna(subset=FEATURE_COLS + ["won"])
            y = test["won"].to_numpy(dtype=float)
            p = np.asarray(pred, dtype=float)
            ys.append(y)
            ps.append(p)
            per_season.append(
                {
                    "season": int(season),
                    "n": int(len(test)),
                    "brier": brier_score(y, p),
                    "log_loss": log_loss_binary(y, p),
                    "ece": expected_calibration_error(y, p, n_bins=args.bins),
                }
            )
        if not ys:
            print("no folds")
            return 1
        y_all = np.concatenate(ys)
        p_all = np.concatenate(ps)
        ece = expected_calibration_error(y_all, p_all, n_bins=args.bins)
        result = {
            "seasons": seasons,
            "n": int(len(y_all)),
            "brier": brier_score(y_all, p_all),
            "log_loss": log_loss_binary(y_all, p_all),
            "ece": ece,
            "verdict": verdict_from_ece(ece, int(len(y_all))),
            "bins": calibration_table(y_all, p_all, n_bins=args.bins),
            "per_season": per_season,
        }
        print(
            "calibration n={n} brier={brier:.4f} log_loss={log_loss:.4f} "
            "ece={ece:.4f} verdict={verdict}".format(**result)
        )
        for row in per_season:
            print(
                "  season {season}: n={n} ece={ece:.4f} brier={brier:.4f}".format(**row)
            )
        _maybe_json(args.json_out, result)
        return 0

    if args.cmd == "leakage-audit":
        from sports_ds.audit.leakage import audit_pregame_form_features
        from sports_ds.data.nfl import load_team_game_panel

        seasons = _parse_seasons(args.seasons)
        panel = load_team_game_panel(seasons)
        result = audit_pregame_form_features(panel)
        print(f"leakage audit: {result['status']}")
        for c in result.get("checks", []):
            print(f"  {c.get('name')}: {'PASS' if c.get('pass') else 'FAIL'}")
        if result.get("errors"):
            for e in result["errors"]:
                print(f"  error: {e}")
        _maybe_json(args.json_out, result)
        return 0 if result.get("status") == "CLEAN" else 2

    if args.cmd == "nfl-eda":
        from sports_ds.data.nfl import load_team_game_panel
        from sports_ds.eda.summary import format_summary, summarize_team_game_panel

        seasons = _parse_seasons(args.seasons)
        panel = load_team_game_panel(seasons)
        print(format_summary(summarize_team_game_panel(panel)))
        return 0

    if args.cmd == "nba-eda":
        from sports_ds.data.nba import load_nba_team_game_panel
        from sports_ds.eda.summary import format_summary, summarize_team_game_panel

        seasons = _parse_seasons(args.seasons)
        panel = load_nba_team_game_panel(seasons)
        print(format_summary(summarize_team_game_panel(panel)))
        return 0

    if args.cmd == "nba-win-pipeline":
        from sports_ds.pipelines.nba_win_model import format_nba_win_report, run_nba_win_pipeline

        seasons = _parse_seasons(args.seasons)
        result = run_nba_win_pipeline(seasons=seasons, min_train_seasons=args.min_train_seasons)
        print(format_nba_win_report(result))
        _maybe_json(args.json_out, result)
        return 0

    return 1


def _maybe_json(path: str, result: dict, drop_keys: tuple[str, ...] = ()) -> None:
    if not path:
        return
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {k: v for k, v in result.items() if k not in drop_keys}
    out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"\nwrote {out}")


def _parse_seasons(raw: str) -> list[int]:
    raw = raw.strip()
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


if __name__ == "__main__":
    raise SystemExit(main())
