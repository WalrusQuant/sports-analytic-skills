#!/usr/bin/env python3
"""Print a sports data source plan template for a modeling question."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """# Data source plan

Question:
Sport/league:
Grain needed:
Historical depth:
Primary source/package:
Fallback:
Fields required at T:\nKnown coverage gaps:
License/ToS notes:
Next skill: nflreadpy | sportsdataverse-py | pybaseball
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
