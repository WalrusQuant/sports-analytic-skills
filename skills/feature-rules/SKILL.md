---
name: feature-rules
description: Define, review, and document point-in-time legal sports-model features. Use when creating rolling form, rest, matchup, rating, roster, injury, or contextual predictors.
metadata:
  version: "0.12.0"
---

# Feature Rules

## Outcome

Produce a feature inventory reproducible from information available at the
declared prediction decision time T. Every feature needs its source, grain,
availability rule, transform, lookback, shift, null policy, legality verdict,
and evidence. Both raw inputs and every transformation must be legal at T.

## Prediction contract and legality test

Before construction, write the target, row grain, exact T (kickoff, lineup
lock, first pitch, or instant before an in-game event), source publication and
revision policy, eligible population, and historical reconstruction rule.
“Game day” is too vague when lineups, injuries, weather, or prices change.

Ask of every historical value:

> Could an analyst following the declared data policy compute this exact value
> from information published at or before T?

| Finding | Action |
|---|---|
| source and transform known by T | legal candidate |
| source arrives with stable delay | shift by delay; document it |
| only part is known | encode only known portion |
| availability unknown | `REVIEW REQUIRED`; never pass |
| post-T source or transform | illegal; drop or redefine T |

Read [the legality matrix](references/legality_matrix.md) while classifying
feature families, [the shift patterns](references/shift_patterns.md) while
implementing temporal transforms, and
[the feature-card template](references/feature_card_template.md) while
documenting the final inventory.

## Workflow

1. Declare target, grain, T, population, and publication policy.
2. Inventory sources, stable IDs, event time, publication time, and revisions.
3. Classify every source as known, delayed, conditional, unknown, or post-T.
4. Specify transforms in plain language before coding.
5. Construct history with explicit sort, shift, and lookback or as-of join.
6. Construct opponent/context features from already time-safe values.
7. Define early-history, missingness, staleness, and offseason behavior.
8. Fit preprocessing, selection, encoding, and reduction inside each fold.
9. Preview values/null rates and test boundary rows manually.
10. Issue verdicts and remediate failures before modeling.

## Feature-family decision table

| Feature | Pre-event status | Required evidence |
|---|---|---|
| Home/venue | usually legal | schedule version known by T |
| Prior form | legal if shifted | event ordering and finalization rule |
| Rest days | usually legal | prior event and schedule snapshot |
| Rating difference | legal if updated after prior events | update trace and initialization |
| Opponent strength | legal if opponent value is pre-event | validated as-of opponent join |
| Injury/availability | conditional | historical publication timestamp |
| Expected lineup | conditional | snapshot at/before T |
| Market price | conditional | quote timestamp and cutoff |
| Weather | conditional | forecast vintage, not final observation |
| Current score/stats | illegal pre-event | target-only or redefine T |
| Final-season aggregate | illegal for earlier rows | expanding prior value |
| Full-data target encoding | illegal | training-fold fit only |

## Construction patterns

### Shift, then aggregate

```python
panel = panel.sort_values(["team", "event_time", "game_id"])
g = panel.groupby("team", sort=False)["won"]
panel["pre_win_pct"] = g.transform(
    lambda s: s.shift(1).expanding(min_periods=1).mean()
)
panel["roll5_win_pct"] = g.transform(
    lambda s: s.shift(1).rolling(5, min_periods=1).mean()
)
# Wrong: current label enters current feature.
panel["leaky_roll5"] = g.transform(lambda s: s.rolling(5).mean())
```

Make tie-break ordering explicit. Input row order is not a chronology.

### Publication-time as-of joins

```python
left = events.sort_values(["decision_time", "team"])
right = ratings.sort_values(["published_at", "team"])
joined = pd.merge_asof(
    left, right, left_on="decision_time", right_on="published_at",
    by="team", direction="backward", allow_exact_matches=True,
)
assert joined["published_at"].le(joined["decision_time"]).all()
```

Event date alone is insufficient. Never backfill a missing historical record
with a later publication; define maximum staleness where old data should expire.

### Opponent joins and differentials

Build team priors first, then join the opponent's already-safe same-event row.

```python
opp = team_features[["game_id", "team", "pre_win_pct", "rating"]].rename(
    columns={"team": "opponent", "pre_win_pct": "opp_pre_win_pct",
             "rating": "opp_rating"}
)
feat = team_features.merge(opp, on=["game_id", "opponent"], validate="one_to_one")
feat["win_pct_diff"] = feat["pre_win_pct"] - feat["opp_pre_win_pct"]
feat["rating_diff"] = feat["rating"] - feat["opp_rating"]
```

Assert distinct entities, one-to-one cardinality, shared game identity, and no
current outcome fields on either side.

### Rest, minimum history, and priors

```python
panel = panel.sort_values(["team", "event_time", "game_id"])
panel["rest_days"] = (
    panel.groupby("team")["event_time"].diff().dt.total_seconds() / 86400
)
panel["pre_games_played"] = panel.groupby("team").cumcount()
model_df = panel.loc[
    panel["pre_games_played"].ge(3)
    & panel["opp_pre_games_played"].ge(3)
].copy()
```

First events, offseason gaps, doubleheaders, postponements, and same-day events
need explicit rules. Choose missing, league/hierarchical prior, carryover, or
exclusion before evaluation. Never use zero silently when it has meaning.

### Fold-fitted transformations

Imputation, scaling, categorical and target encoding, supervised selection,
PCA, and embeddings are feature construction. Fit them on each chronological
training fold only, then transform that fold's test rows. A shifted source can
still leak through a full-data scaler or selector.

## Diagnostics and invariants

- First entity event has no empirical prior unless a documented prior supplies it.
- Changing future outcomes cannot change earlier feature rows.
- Shifted form equals a hand calculation from strictly prior rows.
- Opponent features equal the opponent's same-event pre-event values.
- Every as-of record has `published_at <= T` and acceptable staleness.
- Current target and aliases are absent from candidate features.
- Preprocessing is newly fit per training fold.
- Null rates and eligibility match the early-history specification.

Use a future-perturbation test: alter outcomes after a cutoff, rebuild, and
assert all feature values at or before the cutoff remain unchanged.

## Anti-patterns

| Anti-pattern | Failure | Repair |
|---|---|---|
| roll without shift | current label included | shift first |
| final-season value on early event | future bleeds backward | expanding/as-of |
| display-name joins | duplicate/wrong opponent | stable IDs + cardinality assertion |
| fill on unsorted rows | accidental chronology | sort and assert monotonicity |
| backfill historical gaps | later values move backward | prior/missing/stale rule |
| full-data preprocessing | test distribution leaks | fold-local fit |
| current participation as availability | often known post-T | timestamped snapshot/drop |
| zero-filled early form | invented history | explicit prior/threshold |
| shifted but late-published source | source remains illegal | publication-time policy |

## Standalone helpers

The helpers read user-owned CSV, Parquet, JSON, JSONL, or NDJSON and require
`pandas`. Candidate features are explicit; there is no hidden feature list.

```bash
python /path/to/feature-rules/scripts/feature_preview.py \
  --input features.csv --features pre_win_rate,rest_days,rating_diff \
  --context season,event_id,team --rows 12

python /path/to/feature-rules/scripts/legality_report.py \
  --input feature_catalog.csv --feature-col feature \
  --available-at-col availability --out feature_legality.json
```

The legality input is a catalog with one row per feature—not a modeling matrix.
It requires a unique feature-name column and a timing classification column.
Canonical classifications are `known_by_t`, `delayed`, `conditional`, `unknown`,
and `post_t`; common pregame/pre-decision spelling variants are normalized.
Use `--features` only to select named catalog rows and `--banned` to extend the
exact forbidden-name list. Exact forbidden names or `post_t` fields return
`ILLEGAL` and status 2. Duplicate names, missing/unrecognized classifications,
and unresolved timing return `REVIEW REQUIRED` and status 1. Even an otherwise
passing catalog remains `REVIEW REQUIRED`, because strings cannot prove
timestamps, sorting, joins, shifts, or fold-fitting. `LEGAL` is issued only
after the manual evidence review below.

Minimum catalog:

```csv
feature,availability
pre_win_rate,known_by_t
rest_days,known_by_t
projected_lineup,conditional
```

## Feature card and output contract

```text
Feature name/group and purpose:
Target / row grain / decision time T:
Raw source, version, source grain, and join keys:
Event time / publication time / revision policy:
Transform; sort, shift, lookback, minimum periods:
Opponent/as-of join rule:
Missing, staleness, offseason, and early-history policy:
Fold-fitted components:
Verdict: LEGAL | ILLEGAL | REVIEW REQUIRED
Evidence/tests and required remediation:
Used by models / owner / date:
```

Inventory every model input, not just engineered columns.

## Worked example and integrity rules

For pre-game team form: sort by entity/time/stable event ID; shift outcomes;
compute expanding and rolling form; define prior or three-game threshold; join
the opponent's shifted row; derive differences; hand-check first and midseason
rows; perturb future outcomes; run both helpers; then complete `leakage-audit`.

1. Declare T before construction; unknown availability is not a pass.
2. A shift does not repair a post-T source.
3. Join by stable IDs with asserted cardinality and time bounds.
4. Make null, prior, staleness, and minimum-history behavior explicit.
5. Drop illegal features or redefine the problem; do not merely note them.
