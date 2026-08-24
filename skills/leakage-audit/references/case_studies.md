# Sports Leakage Case Studies

## 1. Rolling form without shift
Symptom: week-1 model uses the week-1 result inside the feature.
Fix: `shift(1)` before rolling/expanding.

## 2. Season EPA on early weeks
Symptom: final-season team EPA predicts week 2 too well.
Fix: expanding as-of only through prior games.

## 3. Opponent stats include current game
Symptom: opp defensive EPA includes points allowed in this game.
Fix: compute opponent priors from past games only, then join.

## 4. Random K-fold “validation”
Symptom: great CV accuracy, dies next season.
Fix: season walk-forward.

## 5. Perfect accuracy
Symptom: ~100% win prediction with box-score features.
Fix: you used the outcome; drop it.
