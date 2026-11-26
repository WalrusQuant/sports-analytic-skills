---
name: ratings-strength-models
description: >
  Build and evaluate sports strength models, including sequential Elo ratings,
  offense/defense splits, power ratings, and strict pre-event matchup features.
  Use for rankings, opponent adjustment, and strong prediction baselines.
license: MIT
metadata:
  version: "1.0.0"
---

# Ratings & Strength Models (Sports)

## Overview

Estimate latent team (or player) strength from **past** results, then use those
ratings only as they existed **before** game T.

Ratings are often the strongest simple sports baselines and strong features for
logistic/ML models. The non-negotiable rule: **as-of only**. Write the loop in
the analysis: read each team's rating before the game, score the game, then update.

---

## When to Use This Skill

Use when:

- Team power ratings / rankings over a season
- Matchup priors for win or margin models
- Opponent adjustment
- Strong baselines before feature-heavy ML
- User says “Elo,” “power ratings,” or “team strength”
- NFL/NBA/MLB Elo baselines

Do **not** use as a substitute for:

| Need | Go to |
|---|---|
| Raw form windows only | `time-series-sports` / `feature-rules` |
| Full ML horse race | `predictive-modeling` |
| Validation design | `validation-design` |
| Season win distributions from ratings | `simulation-sports` |

---

## Setup

The loop below is ordinary pandas. Read `games` from a sportsleader-data URL (`data-sources`). `start_time` is on `games`, not on team rows.

```bash
python3 -m venv .venv
.venv/bin/pip install pandas pyarrow
```

---

## Workflow

1. Choose the **result signal** (win, margin, goal diff, points ratio, EPA, runs).
2. Choose **update style** (sequential Elo-like vs batch season-to-date).
3. Fit/update using **only past games**.
4. Export an **as-of rating** for each team before each game.
5. Predict matchups from rating differentials (+ home).
6. Evaluate with season walk-forward (`validation-design`).
7. Compare to constant / home / form baselines (`baseline-models`).
8. Report params, as-of rule, metrics, limits.
9. Optional: feed into `simulation-sports`.

---

## Model Families

| Family | Best for | Notes |
|---|---|---|
| Elo / Glicko-style | sequential win strength | easy as-of; margin optional |
| Offense/defense split | score models | attack vs defense ratings |
| Least-squares power ratings | season-to-date margins | solve system each week |
| Hierarchical strength | players with uneven n | partial pooling |
| Possession models | pace sports | sport-specific later |

Start with Elo-like or margin power ratings before exotic variants.

Sequential Elo is the reference implementation the agent writes on the user's game table. Glicko, offense/defense, least-squares, hierarchical, margin, and possession models are additional methodology and need their own code.

Read [rating_families.md](references/rating_families.md) when choosing Elo, power ratings, or an
offense/defense model. Read [parameters.md](references/parameters.md) before setting update,
home-advantage, carryover, or margin rules. Read [evaluation.md](references/evaluation.md)
before designing forward scoring and baseline comparisons.

---

## Elo on a game table

Read one completed game per row from sportsleader-data `games` (`season`, `start_time`, `game_id`, `home_team_id`, `away_team_id`, `home_score`, `away_score`). Expected home score, using ratings from **before** the game:

```text
p_home = 1 / (1 + 10 ** (-(elo_home + home_adv - elo_away) / 400))
```

`actual_home` is 1 when the home team wins, 0 when it loses, and 0.5 on a tie. The update is `change = K * (actual_home - p_home)`, then add `change` to the home rating and subtract it from the away rating. Defaults: `K = 20`, `home_adv = 65`, initial rating 1500. Record `elo_pre` and `p_home` before applying `change`. Do not tune `K` or `home_adv` on the final season.

```python
import pandas as pd

games = pd.concat(
    [pd.read_parquet(f"nfl_games_{season}.parquet") for season in (2022, 2023, 2024)],
    ignore_index=True,
)
games = games[games["completed"]].dropna(subset=["home_score", "away_score"])
games = games.sort_values(["season", "start_time", "game_id"])
ratings = {}
k, home_adv, init = 20.0, 65.0, 1500.0
rows = []
for game in games.itertuples(index=False):
    home_pre = ratings.get(game.home_team_id, init)
    away_pre = ratings.get(game.away_team_id, init)
    p_home = 1 / (1 + 10 ** (-(home_pre + home_adv - away_pre) / 400))
    if game.home_score > game.away_score:
        actual = 1.0
    elif game.home_score < game.away_score:
        actual = 0.0
    else:
        actual = 0.5
    rows.append({"game_id": game.game_id, "home_pre": home_pre, "away_pre": away_pre, "p_home": p_home})
    change = k * (actual - p_home)
    ratings[game.home_team_id] = home_pre + change
    ratings[game.away_team_id] = away_pre - change
```

When a charter sets carryover below 1, shrink between seasons with `rating = init + carryover * (rating - init)`. A team-game table is two rows per game: the away pre-game probability is `1 - p_home`. Score those as-of probabilities on later seasons only. The order field must strictly order each team's events.

---

## Design Choices

### K factor
- Higher K: reacts faster, noisier
- Lower K: stabler, slower to adapt
- NFL/NBA starting point: K ≈ 20 on 1500-scale Elo
- Long-season competitions often justify a lower starting K

### Home advantage
- Add `home_adv` to home team pre-game Elo when computing expected score
- Start fixed; estimate later from data if needed

### Margin
- Optional multiplier on K using point differential
- Diminishing returns (log/sqrt) to avoid blowout domination

### Mean reversion / season regression
- Regress ratings toward mean between seasons for multi-year series
- Important for long panels and roster turnover

### Initialization
- Common: all teams 1500
- Report init explicitly

---

## Other Families (patterns)

### Least-squares power ratings (season-to-date)
Each week, solve team strengths from margins-to-date; store as-of ratings before each game. Recompute weekly — never use end-of-season solution for early weeks.

### Offense/defense split
Each team has attack and defense parameters; predict score lines, not only winners. Still as-of only.

### Hierarchical player strength
Partial pooling when player n is uneven (`statistical-modeling` mixed models / Bayesian refs).

---

## Evaluation

**Primary**
- walk-forward log-loss / Brier for win probability from rating diff
- MAE for predicted margin if modeling spreads

**Always compare to in the full methodology**
- constant baseline
- home-only model
- form logistic baseline when available

Always include the 0.5 reference and, after the first season, the prior-season home rate. Home-only logistic, form, or another rating need `baseline-models` or another fold-local fit before they are compared.

**Success**
- beats constant on most folds
- preferably competitive with form logistic

---

## Hard Constraints

1. **As-of only** — never use post-game rating to predict that game.
2. Update order must follow real chronology.
3. Do not fit K on the final test season repeatedly without nested validation.
4. Report initialization and scale (e.g. mean 1500).
5. Do not treat ratings as causal player quality without more structure.
6. Every rating claim must name sport, seasons, event ordering, and parameters.

---

## Anti-Patterns

- Final rating applied backward to early games
- Huge K chasing noise
- Ignoring home advantage
- Mixing playoffs and regular season without a flag
- Claiming ranking quality without forward prediction metrics
- Using form and Elo interchangeably without a bakeoff

---

## Reporting Template

```text
Rating model: Elo
Sport and season numbering:
Signal: win (margin multiplier, if any)
Params: K, home advantage, init (often 1500)
As-of rule: pre-game rating saved before the update
Validation: season walk-forward
Metrics vs constant / home / form logistic:
Calibration:
Limits:
```

---

## Output Contract

Done means:

- [ ] As-of rule stated
- [ ] Params stated
- [ ] Walk-forward metrics vs baselines present
- [ ] Limits stated
- [ ] Repro command present

---

## Worked Examples

For season simulation, pass a documented pre-event probability artifact to
`simulation-sports`; do not treat final ratings as if they existed before
earlier games.

---

## References

### references/
| File | Contents |
|---|---|
| [rating_families.md](references/rating_families.md) | family overview |
| [parameters.md](references/parameters.md) | K, home_adv, margin, regression |
| [evaluation.md](references/evaluation.md) | how to score ratings |

## Related Skills

| Need | Skill |
|---|---|
| Baselines | `baseline-models` |
| Features | `feature-rules` |
| Form windows | `time-series-sports` |
| Predictive ML | `predictive-modeling` |
| Validation | `validation-design` |
| Simulation from ratings | `simulation-sports` |

---
