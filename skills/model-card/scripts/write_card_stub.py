#!/usr/bin/env python3
"""Write a sports model card markdown stub."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """# Model card: {name} ({version})

## Identity

- Name: {name}
- Version: {version}
- Sport:
- Owner:
- Reviewers:
- Status: experimental | evaluated | approved | retired
- Created:
- Next review:

## Intended use

- In scope:
- Intended users and decisions:
- Out of scope:
- Prohibited uses:

## Target and timing

- Target:
- Grain: {grain}
- Prediction decision time:
- Forecast horizon:
- Output semantics:

## Data

- Sources:
- Sport / competition / population:
- Source provenance:
- Window:
- Filters, exclusions, and missingness:
- Sample size:
- Immutable snapshot or artifact:

## Features

- Set / registry names:
- Transformations:
- Time-safety:
- Feature provenance and timing notes:

## Baselines

- Constant / home / Elo / form:
- Candidate family:
- Comparison rule:

## Validation

- Design:
- Fold boundaries and held-out population:
- Primary metric:
- Metric direction:
- Secondary metrics:

## Results

- Mean walk-forward:
- Per-season / per-fold:
- Uncertainty and slices:
- Calibration:
- Leakage and stability findings:

## Limitations and failure modes

- Known limitation or misuse risk:

## Maintenance

- Monitoring owner and cadence:
- Retrain triggers and actions:
- Kill conditions, minimum evidence, and actions:
- Review and approval history:
- Experiments:

## Artifact manifest

- Data / features / configuration / model / metrics / predictions:
- Dependencies and environment:

## Reproduction

```bash
# Fill with the exact commands used.
```
"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--name", default="NAME")
    p.add_argument("--version", default="vVERSION")
    p.add_argument("--grain", default="FILL_ME")
    p.add_argument("--out", default="data/model_card.md")
    args = p.parse_args()
    if args.name.strip() == "":
        p.error("--name must not be empty")
    if args.version.strip() == "":
        p.error("--version must not be empty")
    if args.grain.strip() == "":
        p.error("--grain must not be empty")
    if args.out.strip() == "":
        p.error("--out must not be empty")
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        TEMPLATE.format(name=args.name, version=args.version, grain=args.grain),
        encoding="utf-8",
    )
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
