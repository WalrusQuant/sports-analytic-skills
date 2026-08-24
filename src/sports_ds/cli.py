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

    p_eda = sub.add_parser("nfl-eda", help="Load NFL team-game panel and print EDA summary")
    p_eda.add_argument("--seasons", default="2023-2024")

    args = parser.parse_args(argv)

    if args.cmd == "nfl-win-pipeline":
        from sports_ds.pipelines.nfl_win_model import format_pipeline_report, run_nfl_win_pipeline

        seasons = _parse_seasons(args.seasons)
        result = run_nfl_win_pipeline(seasons=seasons, min_train_seasons=args.min_train_seasons)
        print(format_pipeline_report(result))
        if args.json_out:
            out = Path(args.json_out)
            out.parent.mkdir(parents=True, exist_ok=True)
            # make JSON safe
            payload = {k: v for k, v in result.items() if k != "eda"}
            out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            print(f"\nwrote {out}")
        return 0

    if args.cmd == "nfl-eda":
        from sports_ds.data.nfl import load_team_game_panel
        from sports_ds.eda.summary import format_summary, summarize_team_game_panel

        seasons = _parse_seasons(args.seasons)
        panel = load_team_game_panel(seasons)
        print(format_summary(summarize_team_game_panel(panel)))
        return 0

    return 1


def _parse_seasons(raw: str) -> list[int]:
    raw = raw.strip()
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


if __name__ == "__main__":
    raise SystemExit(main())
