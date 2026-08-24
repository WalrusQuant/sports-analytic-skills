# Miss Taxonomy

| Miss type | Look for | Possible response |
|---|---|---|
| Early-season cold start | low `pre_games_played` | raise min pre-games; prior-season carry |
| Tail overconfidence | p_hat > 0.85 loses | calibration / sharper uncertainty |
| Tail underconfidence | p_hat ~0.55 on blowouts | missing strength signal |
| Home-only edge | away slices fail | home feature leakage or missing road form |
| One-year carry | single fold dominates mean | more seasons; regime check |
| Favorite collapse | high elo/form gap loses | variance / injuries / not modeled |
| Systematic margin scale | residuals fan out | heteroscedastic model or transform |

Always count how often each miss type occurs — anecdotes are not taxonomy.
