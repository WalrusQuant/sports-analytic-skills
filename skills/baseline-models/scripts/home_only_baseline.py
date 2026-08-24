#!/usr/bin/env python3
"""Fit a home-only logistic GLM on NFL team-game panel (pooled train seasons)."""

from __future__ import annotations

import argparse

import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

from sports_ds.data.nfl import load_team_game_panel


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seasons", default="2018-2023")
    args = p.parse_args()

    df = load_team_game_panel(_parse_seasons(args.seasons))
    fit = smf.glm("won ~ is_home", data=df, family=sm.families.Binomial()).fit(cov_type="HC3")
    or_home = float(np.exp(fit.params["is_home"]))
    ci = np.exp(fit.conf_int().loc["is_home"]).astype(float).tolist()
    print(fit.summary())
    print(f"home odds ratio: {or_home:.3f} CI95={ci}")
    print("note: this is pooled-season inference, not walk-forward predictive validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
