# Model Ladder

Climb only with walk-forward evidence.

1. **Constant / mean baseline**  
   If you cannot beat this, you have nothing.

2. **Domain simple model**  
   Home field, Elo/rating difference, average margin differential.

3. **Regularized linear / logistic on clean features**  
   Often the production winner on small/medium sports tabular problems.

4. **Tree ensembles (HistGBM, XGBoost, LightGBM)**  
   Use when nonlinear interactions are real and validated.

5. **Specialized architectures**  
   Tracking models, sequence models, graph models — only with enough data and a clear failure of rung 3–4.

## Promotion rule

A higher rung must improve primary metric on multiple time folds, not one lucky season.
