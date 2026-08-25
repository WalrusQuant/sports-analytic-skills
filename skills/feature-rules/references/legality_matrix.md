# Feature Legality Matrix (Pre-game T)

Use the verdict vocabulary `LEGAL`, `ILLEGAL`, and `REVIEW REQUIRED`. “Usually
legal” is only a starting hypothesis; the project feature card must supply the
listed evidence for its declared T.

| Feature idea | Initial verdict | Evidence or repair |
|---|---|---|
| Prior win % (shifted) | REVIEW REQUIRED | prove stable order and shift-before-aggregate |
| Current game score | ILLEGAL | outcome; redefine T for an in-game task |
| Home flag | REVIEW REQUIRED | prove schedule snapshot known by T |
| Rest days from schedule | REVIEW REQUIRED | prior event and schedule version known by T |
| Opponent final-season EPA | ILLEGAL | replace with expanding/as-of value |
| Player listed inactive at T | REVIEW REQUIRED | needs timestamped source at or before T |
| Opening line at T | REVIEW REQUIRED | needs quote timestamp and declared cutoff |
| Same-drive PBP for pre-snap T | REVIEW REQUIRED | prove event ordering and availability |
| Target encoding over all seasons | ILLEGAL | fit inside training folds only |
