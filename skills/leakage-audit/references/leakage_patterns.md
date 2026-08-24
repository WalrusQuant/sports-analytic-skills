# Sports Leakage Patterns

## Feature-time bugs
- rolling/expanding without shift
- cumulative season stats including current game
- rest days using future schedule changes unknown at T
- player season averages joined onto early appearances without as-of

## Join bugs
- merging final box scores onto schedule before game
- opponent stats computed after groupby on full panel including current row
- sorting wrong before shift (must sort entity + time)

## Split bugs
- random K-fold on games
- standardizing on train+test
- early stopping on true test fold
- leakage through hyperparameter search over the final season

## Label bugs
- using revised official stats that post-date T without noting revision policy
