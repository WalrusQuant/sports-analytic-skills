---
name: eda-sports
description: >
  Exploratory data analysis for user-provided sports data: grain, key integrity,
  coverage, missingness, entity balance, base rates, outliers, structural breaks,
  and leakage red flags. Use before feature engineering or model fitting.
license: MIT
metadata:
  version: "0.12.0"
---

# EDA for Sports Data

## Outcome

Understand the data well enough that the next decision is explicit. Sports EDA
is not one call to `describe()`: it is a structured review of grain, keys, time
coverage, entities, missingness, targets, schedule structure, outliers,
structural breaks, and fields unavailable at prediction time T.

Finish with a written **go**, **repair**, or **stop** decision. A clean EDA
report does not certify that engineered features are time-safe.

## When to Use This Skill

Use when:

- a sports table is new, freshly loaded, or not yet trusted;
- grain, keys, coverage, missingness, or base rates need an honest audit;
- before feature engineering or first model fit;
- a weird model result might just be bad data structure.

Do **not** use this skill as a substitute for:

- formal leakage verdicts → `leakage-audit`;
- feature construction → `feature-rules` / `time-series-sports`;
- source selection → `data-sources`.

| Need | Go instead |
|---|---|
| Choose a public source | `data-sources` |
| Build legal features | `feature-rules` |
| Prove time-safety | `leakage-audit` |
| Charts only | `sports-visualization` |

## Required context

Before calculating summaries, record the question, target, prediction time T,
claimed row grain and key, source/retrieval time, requested period, completion
status, and populations included. If grain or T is ambiguous, resolve it first.

Use [the EDA checklist](references/eda_checklist.md) as the full run sheet. Read
[the grain guide](references/grain_guide.md) when row meaning, keys, or
aggregation are in doubt. Use [the red-flags guide](references/red_flags.md)
when a count, base rate, or model result is odd.

## Workflow

1. Define one row: game, team-game, player-game, play, possession, pitch, or event.
2. Count rows/columns; test natural-key uniqueness and rows per contest.
3. List seasons, weeks/rounds, dates, gaps, partial periods, and active seasons.
4. Count teams/players by season and inspect ID churn and failed joins.
5. Measure missingness overall and by season, source, role, and completion state.
6. Inspect targets, base rates, impossible values, ties, overtime, and zero inflation.
7. Slice meaningful predeclared groups: home/away, phase, role, venue, and era.
8. Find rule, schedule, provider, tracking, definition, and population breaks.
9. Flag fields unavailable at T; reserve the formal verdict for `leakage-audit`.
10. Write findings, repairs, limitations, and the decision.

If grain is wrong or keys are unexplained duplicates, stop before modeling.

## Grain and key diagnostics

| Grain | One row | Typical key | Main trap |
|---|---|---|---|
| Game | one contest | `game_id` | mixing team perspectives |
| Team-game | one team in one contest | `game_id, team` | treating doubled rows as games |
| Player-game | one player in one contest | `game_id, player_id` | ignoring DNP/inactive policy |
| Play/event | one event | `game_id, event_id` | using post-event fields at pre-event T |
| Pitch | one pitch | `game_pk, pitch_no` | unstable event ordering |

```python
key = ["game_id", "team"]
dupes = panel.duplicated(key, keep=False)
print("duplicate key rows:", int(dupes.sum()))
print(panel.loc[dupes].sort_values(key).head(20))
print(panel.groupby("game_id", dropna=False).size().value_counts().sort_index())
```

Do not call `drop_duplicates()` until the cause is known. Repeated pulls,
provider revisions, multiple competitions, and mixed grains need different
repairs. A normal team-game panel usually has two rows per game.

## Coverage and entity balance

```python
coverage = (
    panel.groupby(["season", "week"], dropna=False)
    .agg(rows=("game_id", "size"), games=("game_id", "nunique"),
         teams=("team", "nunique"))
    .reset_index()
)
print(coverage.to_string(index=False))
print(panel.groupby(["season", "team"]).size().unstack(0).fillna(0))
```

Investigate empty periods, low game counts, abrupt entity-count changes, and
the tail of an active season. Imbalance can be real—byes, playoffs, injuries,
promotion/relegation—but can also reveal missing loads. Use stable IDs and a
documented crosswalk for relocations and renames.

The portable coverage helper expects `season`, `week`, `game_id`, and `team`.
Map alternate schemas explicitly:

```bash
python /path/to/eda-sports/scripts/coverage_table.py --input games.csv
python /path/to/eda-sports/scripts/coverage_table.py \
  --input games.parquet --season-col year --period-col round \
  --game-col event_id --team-col club_id
```

## Panel base rates

On a complete two-row team-game panel, overall `won.mean()` is near 0.5 because
each game contributes both perspectives. It is not home advantage.

```python
home = panel.loc[panel["is_home"].eq(1)].copy()
print("overall team-row win rate:", panel["won"].mean())
print("home win rate:", home["won"].mean())
print(home.groupby("season")["won"].mean())
```

Ties, neutral sites, forfeits, incomplete games, and duplicate perspectives can
alter this identity. Explain them rather than forcing the expected value.

## Missingness

Overall rates can hide an era or provider boundary:

```python
critical = [c for c in ["event_time", "points_for", "points_against", "won"] if c in panel]
print(panel[critical].isna().mean().sort_values(ascending=False))
print(panel.groupby("season")[critical].agg(lambda s: s.isna().mean()))
```

Classify each important pattern as structurally expected, temporarily
unavailable, failed collection/join, not applicable, or unknown. Never silently
fill early-history rolling nulls with zero; feature rules must define a prior,
missing indicator, or minimum-history threshold.

## Targets, distributions, and outliers

```python
print(home["point_diff"].describe(percentiles=[.01, .05, .5, .95, .99]))
print(panel["won"].value_counts(dropna=False, normalize=True))
```

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(home["point_diff"].dropna(), bins=40, edgecolor="black", alpha=.85)
ax.axvline(0, color="red", linestyle="--")
ax.set(title=f"Home point differential (n={len(home):,})", xlabel="point differential")
ax.grid(alpha=.25, axis="y")
plt.show()
```

Check scores, margins, counts, and rates against sport semantics. Determine
whether extremes are authentic, unit errors, or duplicates. For count targets,
report zeros and overdispersion; for players, slice by role and playing-time
eligibility before comparing distributions.

## Structural breaks

Before pooling seasons, check rule and overtime changes, schedule length,
shortened seasons, labor disruptions, expansion/relocation, tracking start
dates, provider/schema migrations, definition revisions, and playoff mixing.
A real break may require a known-at-T era flag, separate analyses, a sliding
window, or exclusion. Do not normalize it away without explanation.

## Leakage scouts

For a pre-event task, current-event outcomes and summaries are legal labels but
illegal predictors: current score, margin, result, yards, EPA, win probability,
box-score totals, final-season aggregates, and post-event participation.

```python
suspects = {"points_for", "points_against", "won", "point_diff", "final_score"}
print("present suspects:", sorted(suspects.intersection(panel.columns)))
```

Presence is not failure; use as a pre-event feature is. Keep candidate features
separate and send them through `feature-rules` and `leakage-audit`.

## Automated panel report

`panel_report.py` reads user-owned CSV, Parquet, JSON, JSONL, or NDJSON and
expects `season`, `game_id`, `team`, `is_home`, and binary `won`, with mapping
flags. Install `pandas`; Parquet also needs `pyarrow` or `fastparquet`.

```bash
python /path/to/eda-sports/scripts/panel_report.py \
  --input games.parquet --out data/eda.json
python /path/to/eda-sports/scripts/panel_report.py \
  --input games.csv --out data/eda.json --season-col year \
  --game-col event_id --team-col club --home-col home_flag --outcome-col win
```

Do not guess missing columns. Stop or create an explicit reviewed mapping.
The report uses only the documented EDA decisions: `GO` (status 0), `REPAIR`
(status 1), or `STOP` (status 2). A game without exactly two distinct team rows
and exactly one home row, a null natural key, or a duplicate `(game, team)` key
is structurally incompatible with this helper and returns `STOP`. Missing
outcomes return `REPAIR`; they may be legitimate future events, but must be
separated from completed-event analysis. `GO` still requires the separate time
and leakage reviews described above.

## Red flags

| Symptom | Interpretation | Action |
|---|---|---|
| duplicate natural keys | mixed grain or repeated records | inspect groups; repair cause |
| wrong rows per contest | incomplete/mislabeled panel | rebuild or restate grain |
| entity count jump | real expansion or ID churn | verify and document crosswalk |
| empty periods | incomplete pull or active season | quantify and reload if unexpected |
| constant scores/target | corrupt source or filter | stop and verify source |
| overall win rate near .5 on team-game | expected pairing | use one perspective for game claims |
| early form null | no history | specify prior/minimum history |
| near-perfect first model | leakage until disproved | stop; run `leakage-audit` |

## EDA note template

```text
Question / target / decision time T:
Dataset, source, retrieval/version:
Grain and natural key:
Population and period:
Rows / games / entities:
Key and rows-per-game findings:
Coverage gaps:
Missingness findings:
Target, distribution, and slice findings:
Structural breaks:
Leakage suspects:
Repairs performed / remaining limitations:
Artifacts and plots:
Decision: GO | REPAIR | STOP
Reasons and next action:
```

## Worked example

For a two-season pre-game team win project: declare `(game_id, team)`; run both
helpers; confirm two rows per completed game and expected period coverage;
measure home win rate on home rows; separate future scheduled games from failed
result joins; mark current score/result fields target-only; record era/provider
breaks; and issue `GO` only for the supported population.

## Integrity and resource routing

1. State grain before metrics; never model through unexplained duplicate keys.
2. Never hide incomplete periods, missing entities, or repairs.
3. Compare base rates on the correct independent unit.
4. Preserve raw data and separate outcomes from feature candidates.
5. Use `references/eda_checklist.md` for completeness,
   `references/grain_guide.md` for grain/key questions, and
   `references/red_flags.md` for diagnosis.
6. Run `scripts/coverage_table.py` for coverage and
   `scripts/panel_report.py` for a machine-readable team-game summary.
