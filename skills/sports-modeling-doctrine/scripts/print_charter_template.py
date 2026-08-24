#!/usr/bin/env python3
"""Print or write a sports modeling charter template."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """Question:
Sport/league:
Grain:
Predictive (yes/no):
Decision time T:\nTarget:
Base rate / null:
Baselines:
Primary metric:
Validation:
Data sources:
Out of scope:
"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default="")
    args = p.parse_args()
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(TEMPLATE, encoding="utf-8")
        print(f"wrote {path}")
    else:
        print(TEMPLATE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
