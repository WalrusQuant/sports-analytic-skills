#!/usr/bin/env python3
"""Print or write a sports modeling charter template."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """Question:
Sport/league:
Population:
Grain:
Analysis type:
Predictive (yes/no):
Decision time T:
Target:
Base rate / null:
Baselines:
Primary metric:
Secondary metrics:
Acceptance rule:
Failure conditions:
Validation:
Data sources:
Out of scope:
"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default="")
    args = p.parse_args()
    if args.out:
        if Path(args.out).suffix.lower() not in {".md", ".txt"}:
            p.error("--out must end in .md or .txt")
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(TEMPLATE, encoding="utf-8")
        print(f"wrote {path}")
    else:
        print(TEMPLATE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
