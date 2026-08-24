#!/usr/bin/env python3
"""Write a blank sports model card markdown file."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """# Model card: NAME vVERSION

## Identity
- Name:
- Version:
- Date:

## Intended use
- In scope:
- Out of scope:

## Target and timing
- Target:
- Grain:
- Decision time T:\n\n## Data\n- Sources:
- Window:
- n:\n\n## Features\n- Set:
- Time-safety:

## Baselines
-

## Validation
- Design:
- Primary metric:

## Results
-

## Limits
-

## Maintenance
- Retrain:
- Kill conditions:
- Experiments:
"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default="data/model_card.md")
    args = p.parse_args()
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TEMPLATE, encoding="utf-8")
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
