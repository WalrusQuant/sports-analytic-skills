---
name: model-card
description: >
  Write a durable sports model card covering identity, intended use, target,
  decision time, data, features, baselines, validation, results, limits,
  maintenance, and kill conditions. Use when freezing or sharing a model.
license: MIT
metadata:
  version: "0.12.0"
---

# Sports Model Card

## Outcome

Create a versioned Markdown document tied to user-owned model, data, metrics,
feature, and validation artifacts. A card describes an already evaluated model;
it does not replace the experiment record or make unsupported performance claims.

## Required inputs

- stable model name and version
- owner and review date
- intended and prohibited uses
- sport, grain, target, and decision time
- data provenance, window, filters, and snapshot
- feature definitions and availability timing
- named baselines and validation design
- aggregate and fold-level metrics
- calibration, leakage, fairness, and stability findings as applicable
- serialized model and reproduction instructions

## Required sections

1. Identity and ownership
2. Intended use and out-of-scope uses
3. Target, grain, and prediction timestamp
4. Data sources, window, population, exclusions, and snapshot
5. Features and time-safety rules
6. Baselines and candidate family
7. Validation design and metric definitions
8. Results with uncertainty and slice behavior
9. Known limitations and misuse risks
10. Monitoring, retraining, review, and retirement rules
11. Artifact manifest and reproduction instructions

## Workflow

1. Verify the model version and immutable artifact identifiers.
2. Copy factual fields from experiment and validation artifacts.
3. State intended use narrowly and list explicit prohibited uses.
4. Describe data coverage and known missing populations.
5. Document every feature family and its availability at decision time.
6. Present candidate results beside the declared baseline on identical folds.
7. Summarize calibration, leakage, stability, and error slices.
8. Write operational monitoring and kill conditions.
9. Have a second reviewer trace every claim to an artifact.

## Freeze rules

Freeze a version only when its data snapshot, feature set, configuration, model
file, and validation results are immutable. Any change to those inputs creates a
new version and card. Editorial clarifications may update the document only when
they do not alter the represented model.

## Hard constraints

- Never describe training metrics as expected performance.
- Never omit the baseline or decision time.
- Never claim generality beyond evaluated sports, seasons, and populations.
- Never publish a card without artifact locations and an owner.
- Never leave retirement criteria implicit.

## Helper

```bash
python <path-to-model-card>/scripts/write_card_stub.py --name home-form-logit --version v1 --grain team-game --out data/model_card.md
```

Fill the generated user-owned Markdown file using the artifacts above.

## Resources

- `references/card_template.md` — expanded section template
- `references/kill_conditions.md` — monitoring and retirement triggers
- `scripts/write_card_stub.py` — portable card-stub writer
