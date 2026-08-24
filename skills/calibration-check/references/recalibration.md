# Recalibration Rules

## Allowed
- Platt / isotonic fit on training folds only
- Apply mapping to forward test fold
- Nested walk-forward recalibration experiments

## Forbidden
- Fit mapping on final test labels
- Manual probability edits after outcomes known

## After recalibration
Recompute ECE, Brier, log-loss on true forward folds and report both raw and recalibrated.
