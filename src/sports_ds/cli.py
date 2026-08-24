"""CLI for sports-ds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sports-ds", description="Sports data science toolkit")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_nfl = sub.add_parser("nfl-win-pipeline", help="Run NFL team-win walk-forward pipeline")
    p_nfl.add_argument("--seasons", default="2018-2024")
    p_nfl.add_argument("--min-train-seasons", type=int, default=2)
    p_nfl.add_argument("--json-out", default="")

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
    p_cal.add_argument("--sport", default="nfl", choices=["nfl", "nba", "mlb"])

    p_leak = sub.add_parser("leakage-audit", help="Audit pre-game form feature time-safety")
    p_leak.add_argument("--seasons", default="2023-2024")
    p_leak.add_argument("--json-out", default="")
    p_leak.add_argument("--sport", default="nfl", choices=["nfl", "nba", "mlb"])

    p_eda = sub.add_parser("nfl-eda", help="Load NFL team-game panel and print EDA summary")
    p_eda.add_argument("--seasons", default="2023-2024")

    p_feat = sub.add_parser("feature-registry", help="Print sports_ds feature registry")

    p_rich = sub.add_parser(
        "nfl-win-rich",
        help="NFL rich team-win ladder (EWMA/rest features + logistic/GBM/Elo ensemble)",
    )
    p_rich.add_argument("--seasons", default="2018-2024")
    p_rich.add_argument("--min-train-seasons", type=int, default=2)
    p_rich.add_argument("--k", type=float, default=20.0)
    p_rich.add_argument("--home-adv", type=float, default=65.0)
    p_rich.add_argument("--json-out", default="")

    p_player = sub.add_parser(
        "nfl-player-pipeline",
        help="NFL player-level walk-forward (fantasy/volume targets)",
    )
    p_player.add_argument("--seasons", default="2022-2024")
    p_player.add_argument("--min-train-seasons", type=int, default=1)
    p_player.add_argument("--target", default="fantasy_points_ppr")
    p_player.add_argument(
        "--positions",
        default="QB,RB,WR,TE",
        help="Comma-separated positions",
    )
    p_player.add_argument("--json-out", default="")

    p_player_eda = sub.add_parser("nfl-player-eda", help="NFL player-game panel EDA summary")
    p_player_eda.add_argument("--seasons", default="2023-2024")
    p_player_eda.add_argument("--positions", default="QB,RB,WR,TE")

    p_nba_player = sub.add_parser(
        "nba-player-pipeline",
        help="NBA player-level walk-forward (fantasy/points targets)",
    )
    p_nba_player.add_argument("--seasons", default="2023-2024")
    p_nba_player.add_argument("--min-train-seasons", type=int, default=1)
    p_nba_player.add_argument("--target", default="fantasy_points")
    p_nba_player.add_argument("--positions", default="")
    p_nba_player.add_argument("--min-minutes", type=float, default=5.0)
    p_nba_player.add_argument("--json-out", default="")

    p_nba_player_eda = sub.add_parser("nba-player-eda", help="NBA player-game panel EDA summary")
    p_nba_player_eda.add_argument("--seasons", default="2023-2024")
    p_nba_player_eda.add_argument("--positions", default="")
    p_nba_player_eda.add_argument("--min-minutes", type=float, default=1.0)

    p_mlb_player = sub.add_parser(
        "mlb-player-pipeline",
        help="MLB batter walk-forward via cached boxscores",
    )
    p_mlb_player.add_argument("--seasons", default="2023-2024")
    p_mlb_player.add_argument("--min-train-seasons", type=int, default=1)
    p_mlb_player.add_argument("--target", default="fantasy_points")
    p_mlb_player.add_argument("--positions", default="")
    p_mlb_player.add_argument("--min-pa", type=float, default=1.0)
    p_mlb_player.add_argument(
        "--max-games",
        type=int,
        default=0,
        help="Cap schedule games (0=all). Useful for smokes.",
    )
    p_mlb_player.add_argument("--json-out", default="")

    p_mlb_player_eda = sub.add_parser("mlb-player-eda", help="MLB player-game panel EDA summary")
    p_mlb_player_eda.add_argument("--seasons", default="2024")
    p_mlb_player_eda.add_argument("--positions", default="")
    p_mlb_player_eda.add_argument("--min-pa", type=float, default=1.0)
    p_mlb_player_eda.add_argument("--max-games", type=int, default=0)

    # multi-sport win/margin/elo/eda (NBA + MLB primary; NHL kept for load/eda only)
    for sport in ("nba", "mlb", "nhl"):
        p = sub.add_parser(f"{sport}-eda", help=f"Load {sport.upper()} team-game panel EDA")
        p.add_argument("--seasons", default="2023-2024")
        p2 = sub.add_parser(
            f"{sport}-win-pipeline", help=f"Run {sport.upper()} team-win walk-forward pipeline"
        )
        p2.add_argument("--seasons", default="2023-2024")
        p2.add_argument("--min-train-seasons", type=int, default=1)
        p2.add_argument("--json-out", default="")

    for sport in ("nba", "mlb"):
        pm = sub.add_parser(
            f"{sport}-margin-pipeline",
            help=f"Run {sport.upper()} team-margin walk-forward pipeline",
        )
        pm.add_argument("--seasons", default="2023-2024")
        pm.add_argument("--min-train-seasons", type=int, default=1)
        pm.add_argument("--json-out", default="")

        pe = sub.add_parser(
            f"{sport}-elo", help=f"Run {sport.upper()} Elo as-of baseline walk-forward"
        )
        pe.add_argument("--seasons", default="2023-2024")
        pe.add_argument("--min-train-seasons", type=int, default=1)
        pe.add_argument("--k", type=float, default=20.0 if sport == "nba" else 4.0)
        pe.add_argument("--home-adv", type=float, default=65.0 if sport == "nba" else 20.0)
        pe.add_argument("--json-out", default="")

    args = parser.parse_args(argv)

    if args.cmd == "feature-registry":
        from sports_ds.features.registry import print_feature_registry

        print(print_feature_registry())
        return 0

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
        return _cmd_calibrate(args)

    if args.cmd == "leakage-audit":
        return _cmd_leakage(args)

    if args.cmd == "nfl-eda":
        from sports_ds.data.nfl import load_team_game_panel
        from sports_ds.eda.summary import format_summary, summarize_team_game_panel

        seasons = _parse_seasons(args.seasons)
        print(format_summary(summarize_team_game_panel(load_team_game_panel(seasons))))
        return 0

    if args.cmd == "nfl-win-rich":
        from sports_ds.data.nfl import load_team_game_panel
        from sports_ds.pipelines.team_win_rich import (
            format_team_win_rich_report,
            run_team_win_rich_pipeline,
        )

        seasons = _parse_seasons(args.seasons)
        panel = load_team_game_panel(seasons)
        result = run_team_win_rich_pipeline(
            panel,
            sport="nfl",
            seasons=seasons,
            min_train_seasons=args.min_train_seasons,
            elo_k=args.k,
            elo_home_adv=args.home_adv,
        )
        print(format_team_win_rich_report(result))
        _maybe_json(args.json_out, result, drop_keys=("eda_text",))
        return 0

    if args.cmd == "nfl-player-eda":
        from sports_ds.data.nfl_players import load_player_game_panel

        seasons = _parse_seasons(args.seasons)
        positions = {p.strip().upper() for p in args.positions.split(",") if p.strip()}
        panel = load_player_game_panel(seasons, positions=positions)
        print(
            f"NFL player panel seasons={seasons} positions={sorted(positions)}\n"
            f"rows={len(panel)} players={panel['player_id'].nunique()}\n"
            f"by_pos:\n{panel['position'].value_counts().to_string()}\n"
            f"mean_ppr={panel['fantasy_points_ppr'].mean():.2f} "
            f"median_ppr={panel['fantasy_points_ppr'].median():.2f}"
        )
        return 0

    if args.cmd == "nfl-player-pipeline":
        from sports_ds.pipelines.nfl_player_model import (
            format_nfl_player_report,
            run_nfl_player_pipeline,
        )

        seasons = _parse_seasons(args.seasons)
        positions = {p.strip().upper() for p in args.positions.split(",") if p.strip()}
        result = run_nfl_player_pipeline(
            seasons,
            target_col=args.target,
            positions=positions,
            min_train_seasons=args.min_train_seasons,
        )
        print(format_nfl_player_report(result))
        _maybe_json(args.json_out, result)
        return 0

    if args.cmd == "nba-player-eda":
        from sports_ds.data.nba_players import load_nba_player_game_panel

        seasons = _parse_seasons(args.seasons)
        positions = {p.strip().upper() for p in args.positions.split(",") if p.strip()} or None
        panel = load_nba_player_game_panel(
            seasons, positions=positions, min_minutes=args.min_minutes
        )
        print(
            f"NBA player panel seasons={seasons} positions={sorted(positions) if positions else 'all'}\n"
            f"rows={len(panel)} players={panel['player_id'].nunique()}\n"
            f"by_pos:\n{panel['position'].value_counts().to_string()}\n"
            f"mean_fp={panel['fantasy_points'].mean():.2f} mean_pts={panel['points'].mean():.2f} "
            f"mean_min={panel['minutes'].mean():.1f}"
        )
        return 0

    if args.cmd == "nba-player-pipeline":
        from sports_ds.pipelines.nba_player_model import (
            format_nba_player_report,
            run_nba_player_pipeline,
        )

        seasons = _parse_seasons(args.seasons)
        positions = {p.strip().upper() for p in args.positions.split(",") if p.strip()} or None
        result = run_nba_player_pipeline(
            seasons,
            target_col=args.target,
            positions=positions,
            min_train_seasons=args.min_train_seasons,
            min_minutes=args.min_minutes,
        )
        print(format_nba_player_report(result))
        _maybe_json(args.json_out, result)
        return 0

    if args.cmd == "mlb-player-eda":
        from sports_ds.data.mlb_players import load_mlb_player_game_panel

        seasons = _parse_seasons(args.seasons)
        positions = {p.strip().upper() for p in args.positions.split(",") if p.strip()} or None
        max_games = args.max_games or None
        panel = load_mlb_player_game_panel(
            seasons, positions=positions, min_pa=args.min_pa, max_games=max_games
        )
        print(
            f"MLB player panel seasons={seasons} positions={sorted(positions) if positions else 'hitters'}\n"
            f"rows={len(panel)} players={panel['player_id'].nunique()} max_games={max_games}\n"
            f"by_pos:\n{panel['position'].value_counts().head(12).to_string()}\n"
            f"mean_fp={panel['fantasy_points'].mean():.2f} mean_hits={panel['hits'].mean():.2f} "
            f"mean_pa={panel['plate_appearances'].mean():.2f}"
        )
        return 0

    if args.cmd == "mlb-player-pipeline":
        from sports_ds.pipelines.mlb_player_model import (
            format_mlb_player_report,
            run_mlb_player_pipeline,
        )

        seasons = _parse_seasons(args.seasons)
        positions = {p.strip().upper() for p in args.positions.split(",") if p.strip()} or None
        max_games = args.max_games or None
        result = run_mlb_player_pipeline(
            seasons,
            target_col=args.target,
            positions=positions,
            min_train_seasons=args.min_train_seasons,
            min_pa=args.min_pa,
            max_games=max_games,
        )
        print(format_mlb_player_report(result))
        _maybe_json(args.json_out, result)
        return 0

    if args.cmd in {"nba-eda", "mlb-eda", "nhl-eda"}:
        sport = args.cmd.split("-")[0]
        panel = _load_panel(sport, _parse_seasons(args.seasons))
        from sports_ds.eda.summary import format_summary, summarize_team_game_panel

        print(format_summary(summarize_team_game_panel(panel)))
        return 0

    if args.cmd in {"nba-win-pipeline", "mlb-win-pipeline", "nhl-win-pipeline"}:
        sport = args.cmd.split("-")[0]
        result = _run_sport_win(sport, _parse_seasons(args.seasons), args.min_train_seasons)
        print(result["report"])
        payload = {k: v for k, v in result.items() if k != "report"}
        _maybe_json(args.json_out, payload)
        return 0

    if args.cmd in {"nba-margin-pipeline", "mlb-margin-pipeline"}:
        sport = args.cmd.split("-")[0]
        result = _run_sport_margin(sport, _parse_seasons(args.seasons), args.min_train_seasons)
        print(result["report"])
        payload = {k: v for k, v in result.items() if k != "report"}
        _maybe_json(args.json_out, payload)
        return 0

    if args.cmd in {"nba-elo", "mlb-elo"}:
        sport = args.cmd.split("-")[0]
        result = _run_sport_elo(
            sport,
            _parse_seasons(args.seasons),
            args.min_train_seasons,
            k=args.k,
            home_adv=args.home_adv,
        )
        print(result["report"])
        payload = {k: v for k, v in result.items() if k != "report"}
        _maybe_json(args.json_out, payload)
        return 0

    return 1


def _load_panel(sport: str, seasons: list[int]):
    if sport == "nfl":
        from sports_ds.data.nfl import load_team_game_panel

        return load_team_game_panel(seasons)
    if sport == "nba":
        from sports_ds.data.nba import load_nba_team_game_panel

        return load_nba_team_game_panel(seasons)
    if sport == "mlb":
        from sports_ds.data.mlb import load_mlb_team_game_panel

        return load_mlb_team_game_panel(seasons)
    if sport == "nhl":
        from sports_ds.data.nhl import load_nhl_team_game_panel

        return load_nhl_team_game_panel(seasons)
    raise ValueError(sport)


def _run_sport_win(sport: str, seasons: list[int], min_train_seasons: int) -> dict:
    if sport == "nba":
        from sports_ds.pipelines.nba_win_model import format_nba_win_report, run_nba_win_pipeline

        result = run_nba_win_pipeline(seasons=seasons, min_train_seasons=min_train_seasons)
        result["report"] = format_nba_win_report(result)
        return result
    if sport == "mlb":
        from sports_ds.pipelines.mlb_win_model import format_mlb_win_report, run_mlb_win_pipeline

        result = run_mlb_win_pipeline(seasons=seasons, min_train_seasons=min_train_seasons)
        result["report"] = format_mlb_win_report(result)
        return result
    if sport == "nhl":
        from sports_ds.pipelines.nhl_win_model import format_nhl_win_report, run_nhl_win_pipeline

        result = run_nhl_win_pipeline(seasons=seasons, min_train_seasons=min_train_seasons)
        result["report"] = format_nhl_win_report(result)
        return result
    raise ValueError(sport)


def _run_sport_margin(sport: str, seasons: list[int], min_train_seasons: int) -> dict:
    if sport == "nba":
        from sports_ds.pipelines.nba_margin_model import (
            format_nba_margin_report,
            run_nba_margin_pipeline,
        )

        result = run_nba_margin_pipeline(seasons=seasons, min_train_seasons=min_train_seasons)
        result["report"] = format_nba_margin_report(result)
        return result
    if sport == "mlb":
        from sports_ds.pipelines.mlb_margin_model import (
            format_mlb_margin_report,
            run_mlb_margin_pipeline,
        )

        result = run_mlb_margin_pipeline(seasons=seasons, min_train_seasons=min_train_seasons)
        result["report"] = format_mlb_margin_report(result)
        return result
    raise ValueError(sport)


def _run_sport_elo(
    sport: str,
    seasons: list[int],
    min_train_seasons: int,
    *,
    k: float,
    home_adv: float,
) -> dict:
    if sport == "nba":
        from sports_ds.pipelines.nba_elo_baseline import format_nba_elo_report, run_nba_elo_baseline

        result = run_nba_elo_baseline(
            seasons=seasons, min_train_seasons=min_train_seasons, k=k, home_adv=home_adv
        )
        result["report"] = format_nba_elo_report(result)
        return result
    if sport == "mlb":
        from sports_ds.pipelines.mlb_elo_baseline import format_mlb_elo_report, run_mlb_elo_baseline

        result = run_mlb_elo_baseline(
            seasons=seasons, min_train_seasons=min_train_seasons, k=k, home_adv=home_adv
        )
        result["report"] = format_mlb_elo_report(result)
        return result
    raise ValueError(sport)


def _cmd_leakage(args) -> int:
    from sports_ds.audit.leakage import audit_pregame_form_features

    seasons = _parse_seasons(args.seasons)
    panel = _load_panel(args.sport, seasons)
    result = audit_pregame_form_features(panel)
    print(f"leakage audit ({args.sport}): {result['status']}")
    for c in result.get("checks", []):
        print(f"  {c.get('name')}: {'PASS' if c.get('pass') else 'FAIL'}")
    if result.get("errors"):
        for e in result["errors"]:
            print(f"  error: {e}")
    _maybe_json(args.json_out, result)
    return 0 if result.get("status") == "CLEAN" else 2


def _cmd_calibrate(args) -> int:
    import numpy as np

    from sports_ds.features.team_form import add_pregame_form_features
    from sports_ds.metrics.calibration import (
        calibration_table,
        expected_calibration_error,
        verdict_from_ece,
    )
    from sports_ds.metrics.classification import brier_score, log_loss_binary
    from sports_ds.models.baselines import fit_logistic_baseline
    from sports_ds.pipelines.team_win import FEATURE_COLS
    from sports_ds.validation.splits import season_walk_forward_masks

    seasons = _parse_seasons(args.seasons)
    panel = _load_panel(args.sport, seasons)
    df = add_pregame_form_features(panel)
    df = df.dropna(subset=FEATURE_COLS + ["won"])
    df = df[(df.pre_games_played >= 3) & (df.opp_pre_games_played >= 3)].copy()
    ys, ps, per_season = [], [], []
    for season, tr, te in season_walk_forward_masks(df, min_train_seasons=args.min_train_seasons):
        _, _res, pred = fit_logistic_baseline(df, FEATURE_COLS, tr, te)
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
        "sport": args.sport,
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
        "calibration sport={sport} n={n} brier={brier:.4f} log_loss={log_loss:.4f} "
        "ece={ece:.4f} verdict={verdict}".format(**result)
    )
    for row in per_season:
        print("  season {season}: n={n} ece={ece:.4f} brier={brier:.4f}".format(**row))
    _maybe_json(args.json_out, result)
    return 0


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
