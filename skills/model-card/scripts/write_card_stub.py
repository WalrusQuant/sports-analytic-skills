#!/usr/bin/env python3
"""Write a sports model card markdown stub."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """# Model card: {name} {version}

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
- Grain: team-game
- Decision time T:\n\n## Data\n- Sources:
- Window:
- n:\n- Panel builder:

## Features
- Set / registry names:
- Time-safety:
- `sports-ds feature-registry` notes:

## Baselines
- Constant / home / Elo / form:
- Comparison rule:

## Validation
- Design: season walk-forward
- Primary metric:
- Secondary metrics:

## Results
- Mean walk-forward:
- Per-season / per-fold:
- Calibration:

## Limits
-

## Maintenance
- Retrain:
- Kill conditions:
- Experiments:
- Package commands:
  ```bash
  # fill with exact commands used
  ```
"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--name", default="NAME")
    p.add_argument("--version", default="vVERSION")
    p.add_argument("--out", default="data/model_card.md")
    args = p.parse_args()
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        TEMPLATE.format(name=args.name, version=args.version),
        encoding="utf-8",
    )
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
