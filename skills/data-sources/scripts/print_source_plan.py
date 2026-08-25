#!/usr/bin/env python3
"""Print a sports data source plan template for a modeling question."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """# Data source plan

Question:
Sport / competition / target:
Analytical population:
Analytical grain and natural key:
Decision time T:
Required fields and stable IDs:
Historical depth / coverage window / status handling:
Refresh cadence / completion latency:

## Primary source

Source / release / endpoint:
Rationale:
Native grain and natural key:
Aggregation or join contract to analytical grain:
Event / publication / update / revision semantics:
Coverage evidence to collect:
Authentication / rate / volume constraints:
License / terms / attribution / redistribution:

## Fallback

Source and trigger:
Native grain / key / semantic compatibility:
Known differences requiring a new experiment or caveat:

## Acquisition and verification

Bounded sample query and estimated full volume:
Representative eras / entities / completion states:
Natural-key and row-count checks:
Timestamp / timezone checks:
Cross-source join / crosswalk checks:
Raw snapshot location:
Checksum / schema fingerprint / retrieved_at UTC:
Known gaps and claim limitations:
Fallback activation decision:
EDA handoff:
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
