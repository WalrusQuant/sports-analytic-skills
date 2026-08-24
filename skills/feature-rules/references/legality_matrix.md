# Feature Legality Matrix (Pre-game T)

| Feature idea | Legal? | Notes |
|---|---|---|
| Prior win % (shifted) | Yes | expanding/rolling after shift |
| Current game score | No | outcome |
| Home flag | Yes | known pre-game |
| Rest days from schedule | Yes | if schedule known at T |
| Opponent final-season EPA | No | future unless as-of |
| Player listed inactive at T | Conditional | needs timestamped source |
| Opening line at T | Conditional | needs timestamp ≤ T |
| Same-drive PBP for pre-snap T | Conditional | only if truly pre-snap available |
| Target encoding over all seasons | No | fit inside train folds only |
