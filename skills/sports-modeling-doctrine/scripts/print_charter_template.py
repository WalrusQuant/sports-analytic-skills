#!/usr/bin/env python3
"""Print or write a sports modeling charter template."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """# Sports modeling charter

Question:
Sport / competition:
Population / era / exclusions:
Grain / natural key:
Analysis type: descriptive | explanatory | predictive | causal | ranking | simulation
Decision time T / forecast horizon (if prospective):
Target or estimand / units / label rules:
Paired or dependent rows:
Base rate / null:
Naive and strong simple baselines:
Primary metric / direction:
Secondary metrics:
Validation design / fold construction:
Uncertainty plan:
Data requirements / provenance / minimum coverage:
Acceptance rule:
Failure / revision / stop conditions:
Out of scope / prohibited uses:
Required artifacts:
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
