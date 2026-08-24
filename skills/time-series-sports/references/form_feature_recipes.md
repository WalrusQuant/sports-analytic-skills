# Form Feature Recipes

## Season-to-date win %

```text
sort team, time
won_prior = won.shift(1)
expanding_mean(won_prior)
```

## Last-K point differential

```text
diff_prior = point_diff.shift(1)
rolling(K).mean(diff_prior)
```

## EWMA form

```text
diff_prior = point_diff.shift(1)
ewm(span=S).mean(diff_prior)
```

## Rest days

```text
rest = gameday.diff().days within team
# first game NA or large gap after offseason — handle explicitly
```
