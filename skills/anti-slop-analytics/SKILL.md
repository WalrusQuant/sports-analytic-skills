---
name: anti-slop-analytics
description: >
  Kill analytics presentation slop in sports work: chartjunk, fake certainty,
  cropped axes, vanity dashboards, baseline erasure, metric laundering, and
  unreproducible screenshot science. Use when reviewing figures, tables,
  notebooks, or report visuals for sports modeling — even if the user only says
  "make this look better" or "clean up the charts." Includes slop catalog,
  replacements, and figure audit scripts tied to sports_ds pipeline outputs.
version: "0.5.0"
license: MIT
metadata:
  version: "0.5.0"
---

# Anti-Slop Analytics (Sports)

## Overview

Sports analytics fails in public when visuals lie softer than the text.

This skill enforces honest presentation for sports modeling results. Score each
visual `keep` / `fix` / `kill`.

Works on:

- EDA charts from `sports-visualization`
- walk-forward metric bars from pipeline JSON
- calibration plots
- model cards / README figures
- notebook output dumps

---

## When to Use This Skill

Use when:

- Reviewing charts, tables, dashboards, or notebook outputs
- Preparing figures for README, posts, papers, or model cards
- User asks to “make it look more impressive”
- Suspected vanity metrics or cropped axes
- Pairing with `results-reporting` before publishing

Do **not** use when:

- Designing validation/metrics from scratch → `validation-design`
- Leakage mechanics → `leakage-audit`
- No visual/table exists yet

---

## Slop Catalog (fail these)

1. **Certainty cosplay** — no uncertainty, no sample size, huge font conclusion
2. **Axis crimes** — truncated axes that manufacture drama
3. **Time cherry-pick** — zoom to the winning window only
4. **Metric laundering** — flashy secondary metric hides primary failure
5. **Baseline erasure** — model curve with no reference
6. **Legend fog** — unreadable encodings, 12 colors, no point
7. **Dual-axis trickery** — unrelated series forced into fake correlation
8. **Heatmap theater** — giant correlation mats with no hypothesis
9. **3D / pie distraction** for simple comparisons
10. **Screenshot science** — unreproducible UI grabs as proof
11. **Probabilities as destiny** — 53% shown like a lock
12. **One hot streak highlight reel** as season truth
13. **In-sample cosplay** — training fit shown as walk-forward validation
14. **Sport-context wipe** — no sport/grain/period on the figure

Details: `references/slop_catalog.md`, `references/replacements.md`

---

## Workflow

1. Identify the intended claim of each visual.
2. Check encoding honesty (axes, scales, filters, missing baselines).
3. Check statistical honesty (n, period, uncertainty, selection).
4. Check claim alignment (does visual match the evidence?).
5. Mark each visual: `keep` / `fix` / `kill`.
6. Rewrite titles/captions to state what was measured.
7. Prefer one clear visual over five decorative ones.
8. If the figure comes from a pipeline, require the JSON/command path.

```bash
python skills/anti-slop-analytics/scripts/figure_audit_template.py --out data/figure_audit.md
python skills/anti-slop-analytics/scripts/figure_audit_template.py \
  --title "NBA walk-forward log-loss" \
  --claim "logistic beats constant" \
  --out data/nba_fig_audit.md
```

Good paired commands:

```bash
sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1 --json-out data/nba_win.json
python skills/sports-visualization/scripts/plot_walkforward_metrics.py --json data/nba_win.json
python skills/anti-slop-analytics/scripts/figure_audit_template.py --out data/nba_fig_audit.md
```

---

## Replacement Defaults

| Instead of | Prefer |
|---|---|
| Rainbow equity-style curve only | metric table + baseline deltas + period notes |
| Pie charts for model compare | dot/bar with shared baseline |
| Giant feature importance flex | top drivers + stability caveat |
| Smooth marketing gradient cards | plain tables with n and dates |
| “Insight” callout boxes | falsifiable sentence + limit |
| Single-season hero chart | full walk-forward fold table |

---

## Hard Constraints

1. Never truncate axes to manufacture an effect without explicit warning (default: don’t).
2. Never drop losing segments silently.
3. Never present in-sample curves as validation.
4. Every key figure needs: period, n (or event count), metric definition, sport/grain.
5. If uncertainty is unknown, say unknown — do not draw fake error bars.
6. Baseline required whenever a model claim is made.

---

## Anti-Patterns

- Dashboard makeup on a weak model
- Annotation spam that tells viewers what to feel
- Color as argument
- One magical chart carrying the whole claim
- UI skins over missing method
- Hiding the constant baseline because “it looks worse”

---

## Output Contract

- [ ] Each visual scored keep / fix / kill
- [ ] Specific slop issues named
- [ ] Replacement guidance given
- [ ] Caption/title rewrites where needed
- [ ] Remaining misread risk stated
- [ ] Repro path present or explicitly missing

---

## Worked Example

**Input:** chart titled “Dominant Model” showing cumulative accuracy from one season, y-axis starts at 0.55, no baseline, no sample size.

**Audit:** axis crime + cherry-pick + baseline erasure + overclaim title → `kill`

**Replace with:** walk-forward log-loss vs baselines by season; title “Walk-forward log-loss vs baselines (2019–2024)”.

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win.json
python skills/sports-visualization/scripts/plot_walkforward_metrics.py \
  --json data/nfl_win.json \
  --metric logistic_log_loss \
  --baseline constant_log_loss \
  --out data/nfl_wf.png
```

---

## Bundled Resources

### references/
- `slop_catalog.md`
- `replacements.md`

### scripts/
- `figure_audit_template.py`

---

## Related Skills

- `results-reporting`
- `sports-visualization`
- `calibration-check`
- `model-interpretation`
- `model-card`

---

## Quick Command Card

```bash
python skills/anti-slop-analytics/scripts/figure_audit_template.py --out data/figure_audit.md
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win.json
python skills/sports-visualization/scripts/plot_walkforward_metrics.py --json data/nfl_win.json
```
