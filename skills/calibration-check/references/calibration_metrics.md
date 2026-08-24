# Calibration Metrics (Sports)

## Brier score

Mean squared error of probabilities:

```text
Brier = mean( (p - y)^2 )
```

Lower is better. For a constant base-rate model, Brier ≈ p*(1-p).

## ECE (Expected Calibration Error)

1. Bin predictions
2. For each bin: |mean(p) - mean(y)|
3. Average weighted by bin size

## Reliability curve

X = mean predicted probability in bin  
Y = observed event rate in bin  
Diagonal = perfect calibration

## Pitfalls

- Tiny bins look noisy
- Good log-loss can coexist with local miscalibration
- Pooling seasons can hide regime breaks
