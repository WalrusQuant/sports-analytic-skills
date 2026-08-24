#!/usr/bin/env python3
"""Write a figure/table anti-slop audit template."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """# Figure audit

## Context
- sport/grain:
- analysis command or notebook:
- reviewer:
- date:

For each figure/table:

## Item
- filename/title: {title}
- claim it supports: {claim}
- period:
- n:\n- baseline present (yes/no):
- axis range honest (yes/no):
- uncertainty shown or explicitly unknown:
- in-sample vs walk-forward labeled (yes/no):
- repro path:
- verdict: keep | fix | kill
- issues:
- replacement:
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="data/figure_audit.md")
    ap.add_argument("--title", default="")
    ap.add_argument("--claim", default="")
    args = ap.parse_args()
    if args.out.strip() == "":
        ap.error("--out must not be empty")
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        TEMPLATE.format(title=args.title, claim=args.claim),
        encoding="utf-8",
    )
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
