# Post-load Sanity Checks

Run after the first pull of any new sport/window.

1. Row count > 0
2. Expected seasons present
3. Team-game overall win rate ~ 0.5
4. Home win rate plausible for the sport
5. Score columns not constant
6. Duplicate game ids removed
7. Missingness on key fields documented

If checks fail, do not fit models. Fix source/normalize/filter first.
