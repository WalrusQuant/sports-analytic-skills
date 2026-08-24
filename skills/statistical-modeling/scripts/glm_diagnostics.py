#!/usr/bin/env python3
"""Fit a logistic GLM on sports_ds NFL features and export diagnostics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features


DEFAULT_FORMULA = "won ~ is_home + feature_win_pct_diff + feature_diff_diff + feature_roll3_win_diff"


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def build_model_frame(seasons: list[int], min_pre_games: int = 3) -> pd.DataFrame:
    panel = load_team_game_panel(seasons)
    df = add_pregame_form_features(panel)
    cols = [
        "won",
        "is_home",
        "feature_win_pct_diff",
        "feature_diff_diff",
        "feature_roll3_win_diff",
        "feature_roll5_diff_diff",
        "pre_games_played",
        "opp_pre_games_played",
        "season",
        "week",
        "team",
        "game_id",
    ]
    out = df.dropna(subset=[c for c in cols if c in df.columns]).copy()
    out = out[(out["pre_games_played"] >= min_pre_games) & (out["opp_pre_games_played"] >= min_pre_games)]
    return out


def logistic_diagnostics_report(df: pd.DataFrame, formula: str = DEFAULT_FORMULA) -> dict:
    fit = smf.glm(formula=formula, data=df, family=sm.families.Binomial()).fit(cov_type="HC3")
    params = fit.params.to_dict()
    conf = fit.conf_int()
    odds = {
        k: {
            "coefficient": float(params[k]),
            "odds_ratio": float(np.exp(params[k])),
            "ci95": [float(np.exp(conf.loc[k, 0])), float(np.exp(conf.loc[k, 1]))],
            "pvalue": float(fit.pvalues[k]),
        }
        for k in params.keys()
    }
    mu = np.asarray(fit.fittedvalues, dtype=float)
    y = df["won"].to_numpy(dtype=float)
    # simple calibration buckets
    bins = np.linspace(0, 1, 11)
    digit = np.digitize(mu, bins) - 1
    calib = []
    for b in range(10):
        mask = digit == b
        if mask.sum() == 0:
            continue
        calib.append(
            {
                "bin": b,
                "n": int(mask.sum()),
                "pred_mean": float(mu[mask].mean()),
                "obs_rate": float(y[mask].mean()),
            }
        )

    report = {
        "n": int(len(df)),
        "formula": formula,
        "pseudo_rsquared_mcfadden": float(1 - fit.llf / fit.llnull) if fit.llnull else None,
        "llf": float(fit.llf),
        "aic": float(fit.aic),
        "bic": float(fit.bic),
        "odds_ratios": odds,
        "calibration_bins": calib,
        "summary_text": str(fit.summary()),
    }
    return report


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seasons", default="2018-2023")
    p.add_argument("--formula", default=DEFAULT_FORMULA)
    p.add_argument("--out", default="data/glm_diagnostics.json")
    args = p.parse_args()

    seasons = _parse_seasons(args.seasons)
    df = build_model_frame(seasons)
    report = logistic_diagnostics_report(df, formula=args.formula)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # summary_text can be huge; keep it
    out.write_text(json_dumps(report), encoding="utf-8")
    print(f"n={report['n']} aic={report['aic']:.1f} formula={report['formula']}")
    print("odds ratios:")
    for k, v in report["odds_ratios"].items():
        if k == "Intercept":
            continue
        print(f"  {k}: OR={v['odds_ratio']:.3f} CI={v['ci95']} p={v['pvalue']:.4g}")
    print(f"wrote {out}")
    return 0


def json_dumps(obj) -> str:
    return json.dumps(obj, indent=2)


# late import style-safe
import json  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
