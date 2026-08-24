# Split Patterns for Sports

## Season walk-forward (default)

```text
train seasons < S → test S
```

## Sliding window

```text
train last K seasons → test next season
```

Use after major rule/style shifts.

## Week walk-forward

Inside a season for high-frequency labels. Features must still be shift-safe.

## Embargo

Leave a time gap when labels/features finalize after event time.

## Never

- Shuffle all games, 5-fold CV, report mean accuracy as proof
- Train on 2018–2024, test on 2023
- Use future opponent information unknown at T
