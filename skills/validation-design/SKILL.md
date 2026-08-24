---
name: validation-design
description: >
  Design time-safe validation for sports models: walk-forward splits,
  embargoes, regime awareness, and metric plans. Use before training or
  when a backtest needs a trustworthy evaluation design.
version: "0.1.0"
license: MIT
---

# Validation Design

Modeling-spine skill that locks how sports models are evaluated before
results can be trusted. Chronology is the default; random splits are guilty
until proven innocent.

## When to use

- Before training candidates for a paper claim
- User asks for train/test split advice on sports data
- Replacing random K-fold on games/seasons
- Defining walk-forward, expanding windows, or embargo gaps
- Setting metric plan tied to the decision

## When not to use

- Feature legality details → `feature-rules` / `leakage-audit`
- Baseline selection → `baseline-models`
- Final narrative claim gate → `doctrine`
- Calibration deep-dive → `calibration-check` / `risk`

## Required inputs

Minimum:

- Prediction timestamp rule T
- Target + grain
- Historical time span available
- Claim level sought (`explore` / `paper` / `market-relative`)

Optional:

- Season/regime boundaries
- Sample size constraints
- Production retraining cadence

## Default stance

For almost all sports event prediction:

- Order by time
- Train on past → validate on future
- Re-run across multiple forward steps
- Keep a final untouched holdout if enough history exists

Random row K-fold is inappropriate for standard pre-event prediction.

## Validation patterns

### 1) Walk-forward (default)

- Fold i train: events with time < t_i
- Fold i test: events in [t_i, t_{i+1})
- Step through seasons or month/week blocks

### 2) Expanding window

- Train from origin to t_i, test next block
- Good when early history is scarce but still relevant

### 3) Sliding window

- Train only recent W history before each test block
- Use when regimes shift and ancient history hurts

### 4) Embargo / gap

- Leave a gap between train and test when labels or features settle late
- Required when post-event corrections or delayed reports exist

### 5) Grouped time splits

- Group by event/game ID so related rows do not cross splits
- Player-game rows from the same event stay together

### 6) Final holdout

- Last season/block sealed until one end evaluation
- Not for repeated peeking

## Procedure

1. **Confirm task chronology**
   - Pre-event, in-game, or post-event analytical?
   - Choose split family accordingly

2. **Choose primary metrics before fitting**
   - Probabilistic: log-loss, Brier
   - Continuous: MAE/RMSE + bias
   - Decision-aware metrics only if decision rule is explicit
   - Secondary metrics allowed; primary locked first

3. **Pick split scheme**
   - Default walk-forward by season or date block
   - Add group constraints by event ID
   - Add embargo if needed

4. **Define regime slices in advance**
   - Seasons, rule-change eras, pre/post structural breaks
   - Report performance by slice, not only pooled

5. **Lock tuning rules**
   - Hyperparams tuned inside training folds only
   - No retuning on final holdout repeatedly
   - Early stopping must not peek across the fold boundary improperly

6. **Sample-size sanity**
   - If test blocks are tiny, widen blocks or demote claim level
   - Do not manufacture certainty from 30 events

7. **Write the validation charter**
   - Split diagram in words
   - Metrics
   - Tuning scope
   - Success threshold vs baselines
   - Failure conditions

8. **Only then train/evaluate**
   - Hand off execution to modeling code
   - After results: `doctrine` verdict, maybe `backtest-critique`

## Hard constraints

- Never random-split time-ordered sports events by default
- Never choose the split method after seeing which one makes the model win
- Never tune on the final holdout
- Never pool regimes to hide failures without reporting slices
- Never claim robustness from a single test season unless data forces it (and then claim level stays humble)
- Success thresholds must be stated relative to baselines

## Anti-patterns

- **K-fold cosplay** on games
- **Shuffle then scale then split** pipelines that bleed info
- **Holdout tourism:** repeat visits to the “final” season
- **Metric fishing after results**
- **One giant test set with no walk-forward path for production realism**
- **Ignoring event grouping** so half a game’s rows train and half test
- **Optimistic early stopping** using true test labels indirectly

## Output contract

Done means:

- [ ] Task chronology stated
- [ ] Primary metrics locked
- [ ] Split scheme specified (including grouping/embargo)
- [ ] Regime slices predefined
- [ ] Tuning rules locked
- [ ] Success threshold vs baselines stated
- [ ] Validation charter written before candidate worship
- [ ] Claim-level implications noted if history is short

## Handoffs

- `baseline-models` — evaluate baselines under this charter
- `feature-rules` / `leakage-audit` — ensure inputs match split time safety
- `backtest-critique` — review results produced under (or without) a charter
- `doctrine` — convert outcomes into ship/revise/kill
- `calibration-check` — probability quality on forward folds
- `experiment-log` — store charter + results
- **Stop** if no honest split is possible with available data; stay `explore`

## Worked example

**Request:** “We have 8 seasons of team-game data. Split it for a home-win model.”

1. Chronology: pre-event.
2. Metrics: log-loss primary, Brier secondary.
3. Scheme: walk-forward by season; train past seasons → test next season.
4. Grouping: game-level rows already unique by game ID.
5. Embargo: none if all features are pre-event final; else gap for delayed stats.
6. Holdout: optional final season sealed after model family chosen on earlier folds.
7. Success: beat Tier A base rate and Tier B rating model on log-loss in ≥ majority of forward seasons, no single-season-only miracle.
8. Charter written before XGBoost tuning begins.

## References

- Doctrine evidence hierarchy: `skills/doctrine`
- Baselines: `skills/baseline-models`
- Leakage: `skills/leakage-audit`
