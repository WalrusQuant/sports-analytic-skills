---
name: results-reporting
description: >
  Report sports analysis and modeling results with the question, data, methods,
  validation, baselines, metrics, interpretation, limits, figures, and
  reproduction pointers. Use for research notes, reports, and final answers.
license: MIT
metadata:
  version: "0.12.0"
---

# Results Reporting

## Outcome

Turn user-owned metrics and analysis artifacts into an honest report. The report
must distinguish observed facts from interpretation and make every quantitative
claim traceable to data, validation, and reproduction artifacts.

## Required artifact schema

The bundled renderer accepts JSON with this minimum shape:

```json
{
  "title": "Home-form win model",
  "question": "Does prior form improve held-out win probability estimates?",
  "data": {"sport": "NFL", "grain": "team-game", "period": "2021-2023", "n": 8160},
  "methods": {"target": "won", "baseline": "constant rate", "candidate": "logistic"},
  "validation": {"design": "season walk-forward", "primary_metric": "log_loss"},
  "results": {"baseline_log_loss": 0.693, "candidate_log_loss": 0.681},
  "interpretation": "The candidate improved held-out log-loss modestly.",
  "limits": ["Public injury information was not included."],
  "reproduction": {
    "artifacts": ["data/metrics.json", "data/predictions.csv"],
    "command": "python run_analysis.py --config analysis.json"
  }
}
```

Additional fields are allowed. The renderer requires `data.grain`, positive
`data.n`, `methods.baseline`, `validation.design`,
`validation.primary_metric`, non-empty results and reproduction objects, and a
non-empty limits list. Reproduction metadata may contain whatever the user
actually has; do not invent a command. The renderer does not import any modeling
package.

## Workflow

1. Lock the exact question and decision time.
2. Inventory data, model, metrics, figure, and audit artifacts.
3. Verify that candidate and baseline use identical held-out rows.
4. State sport, grain, period, sample size, filters, and missingness.
5. Describe methods at the level needed to reproduce them.
6. Report primary metric first, with baseline and uncertainty or fold spread.
7. Separate aggregate, fold-level, slice, and calibration results.
8. Interpret magnitude and stability without causal overreach.
9. List limitations, failed checks, and unsupported uses.
10. Include exact artifact paths and commands supplied by the user.

## Metric rules

- Probability models: log-loss or Brier first; accuracy only as secondary context.
- Continuous targets: MAE or RMSE with a constant or simple domain baseline.
- Counts: report the score appropriate to the fitted distribution and a naive count baseline.
- Rankings: report stability and uncertainty, not only order.
- Always provide sample size and direction of improvement.

## Hard constraints

- Never report only the best fold or best seed.
- Never compare metrics computed on different populations without disclosure.
- Never call a model calibrated from discrimination metrics alone.
- Never omit negative, null, or failed results.
- Never manufacture reproduction commands that are absent from the artifacts.

## Helper

```bash
python <path-to-results-reporting>/scripts/render_results_report.py --json data/results.json --out data/results_report.md
```

## Output contract

Return an executive result, question, data, methods, validation, baseline,
results table, interpretation, limitations, artifact manifest, and reproduction
instructions. Use the templates in `references/templates.md` for narrative forms.

## Resources

- `references/templates.md` — concise and full report templates
- `references/writeup_checklist.md` — final quality gate
- `scripts/render_results_report.py` — validated JSON-to-Markdown renderer
