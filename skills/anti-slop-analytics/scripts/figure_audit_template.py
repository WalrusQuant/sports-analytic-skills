#!/usr/bin/env python3
"""Write a figure/table anti-slop audit template."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """# Figure audit

For each figure/table:

## Item
- filename/title:
- claim it supports:
- period:
- n:\n- baseline present (yes/no):
- axis range honest (yes/no):
- uncertainty shown or explicitly unknown:
- verdict: keep | fix | kill
- issues:
- replacement:
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="data/figure_audit.md")
    args = ap.parse_args()
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TEMPLATE, encoding="utf-8")
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
