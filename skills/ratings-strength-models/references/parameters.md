# Elo Parameter Guide

| Param | Role | Starting point (NFL-ish) |
|---|---|---|
| init | starting rating | 1500 |
| K | update speed | 20 |
| home_adv | home Elo points added pre-game | 65 |
| margin mult | blowout dampening | log(abs(diff)+1) |

## Notes
- Tune K only inside training folds
- Home_adv can be fit later; fixed is fine for v1
- Season regression toward mean helps multi-year panels
