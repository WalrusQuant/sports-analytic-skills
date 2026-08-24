#!/usr/bin/env python3
"""Write a sports model card markdown stub."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """# Model card: {name} ({version})

## Identity

- Name: {name}
- Version: {version}
- Date:
- Sport:
- Owner:

## Intended use

- In scope:
- Out of scope:

## Target and timing

- Target:
- Grain: {grain}
- Prediction decision time:

## Data

- Sources:
- Window:
- Population and exclusions:
- Sample size:
- Snapshot or artifact:

## Features

- Set / registry names:
- Time-safety:
- Feature provenance and timing notes:

## Baselines

- Constant / home / Elo / form:
- Comparison rule:

## Validation

- Design:
- Primary metric:
- Secondary metrics:

## Results

- Mean walk-forward:
- Per-season / per-fold:
- Calibration:
- Leakage and stability findings:

## Limits

- Known limitation or misuse risk:

## Maintenance

- Retrain:
- Kill conditions:
- Experiments:
- Artifact manifest:

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
