#!/usr/bin/env python3
"""Write a blank sports validation charter markdown file."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """# Validation charter

- Target:
- Grain:
- Decision time T:\n- Primary metric:
- Secondary metrics:
- Baselines:
- Split: season walk-forward
- min_train_seasons: 2
- Window: expanding
- Tune: inside training only
- Success rule: beat baselines on mean primary metric AND on majority of folds
- Leakage checks: feature-rules + leakage-audit
- Reporting: per-fold table + mean + decision
- Notes:
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
