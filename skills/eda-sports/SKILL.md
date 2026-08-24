---
name: eda-sports
description: >
  Exploratory data analysis for sports datasets: coverage, missingness,
  distributions, leakage/season structure, outliers, and leakage red flags.
  Use after loading data and before serious modeling.
version: "0.1.0"
license: MIT
---

# EDA for Sports

Data analysis skill for understanding sports tables before modeling.

## When to use

- New dataset/season extract just loaded
- Before feature engineering or model fitting
- Debugging weird model performance
- Checking schedule/PBP/roster joins

## When not to use

- Environment/package install → `environment-setup`
- Final model evaluation design → `validation-design`
- Pretty final figures for a report → `sports-visualization`

## Required inputs

- Loaded frame(s)
- Grain expected (game, player-game, pbp, …)
- Time fields (date, season, week, timestamp)
- Target candidate(s) if known

## Procedure

1. **Shape & keys**
   - rows/cols, primary keys, duplicate rate
2. **Time coverage**
   - seasons, weeks, missing dates, lockouts/short seasons
3. **Entity coverage**
   - teams/players present, join failure rates
4. **Missingness**
   - by column and by season
5. **Distributions**
   - targets, minutes/snaps/attempts, scores, pace proxies
6. **Leakage scouts**
   - columns that look like outcomes for pre-event tasks
7. **Segment slices**
   - home/away, season phase, position groups if relevant
8. **Write EDA notes**
   - what is usable, what is broken, what needs repair

## Hard constraints

- Always report grain and time range
- Never skip duplicate-key checks on schedule/PBP merges
- Flag post-event fields when task is pre-event
- Quantify missingness; don’t hand-wave

## Anti-patterns

- `df.describe()` only and done
- Plotting without stating grain
- Ignoring season structural breaks
- Silent row drops

## Output contract

- [ ] Coverage summary
- [ ] Key/duplicate findings
- [ ] Missingness summary
- [ ] Target distribution notes
- [ ] Leakage suspects listed
- [ ] Go / repair / stop recommendation

## Handoffs

- `feature-rules` if clean enough
- `data-sources` / package skill if wrong table
- `sports-visualization` for deeper plots
- `leakage-audit` if suspects are serious

## Example checks (pandas/polars)

```python
# coverage
df.group_by("season").len()
# dup keys
df.select(key_cols).is_duplicated().sum()
# missingness
df.null_count()
```

## References

- package skills for loads
- `feature-rules`, `validation-design`
