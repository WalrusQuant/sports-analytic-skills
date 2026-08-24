#!/usr/bin/env python3
"""Write a blank leakage audit report markdown file."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """# Leakage audit

- Target:
- Grain:
- Decision time T:\n- Feature count:
- Splits:

## Findings

1. [PASS/REVIEW/FAIL]
2. [PASS/REVIEW/FAIL]

## Contaminated fields

-

## Required fixes

-

## Automated script results

-

## Verdict
\nCLEAN | REVIEW REQUIRED | NOT CLEAN

- Auditor:
- Date:
"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True, help="Markdown output path")
    args = p.parse_args()
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TEMPLATE, encoding="utf-8")
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
