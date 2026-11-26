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
logistic/ML models. The non-negotiable rule: **as-of only**.

Bundled standalone path:

- standalone sequential rating construction
- held-out evaluation against simple baselines

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

## Installation

The standalone Elo builder and evaluator require pandas:

```bash
python -m pip install pandas
```

Parquet input also needs `pyarrow` or `fastparquet`.

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

Read one row per completed game. sportsleader-data `games` already has `season`, `game_date`, `game_id`, `home_team_id`, `away_team_id`, `home_score`, and `away_score`. Filter `completed` and non-null scores. `start_time` orders same-day games.

Save both teams' pre-event ratings before updating either one. A useful team-game output includes `team_id`, `opponent_id`, `is_home`, `elo_pre`, raw rating difference, home-adjusted difference, `win_probability`, and the actual result. Ties update as 0.5/0.5.

The order field must strictly order each team's events. Score home rows once per game. Report season-level Elo log loss, Brier score, and accuracy against a fixed 0.5 reference and, after the first season, a home-win rate estimated only from prior seasons. A supplied legal baseline probability can be scored on the same rows. This is a score table for as-of probabilities, not a license to tune K on the final season.

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

## Bundled Resources

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
