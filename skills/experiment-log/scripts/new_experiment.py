#!/usr/bin/env python3
"""Create a new experiment log markdown stub with a timestamped ID."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--slug", default="run")
    p.add_argument("--sport", default="")
    p.add_argument("--out-dir", default="data/experiments")
    args = p.parse_args()

    slug = args.slug.strip().lower()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        p.error("--slug must be lowercase kebab-case")
    if args.out_dir.strip() == "":
        p.error("--out-dir must not be empty")

    now = datetime.now(timezone.utc)
    out_dir = Path(args.out_dir)
    prefix = f"{now.strftime('%Y%m%d')}-{slug}-"
    sequences = []
    for existing in out_dir.glob(f"{prefix}*.md"):
        suffix = existing.stem.removeprefix(prefix)
        if suffix.isdigit():
            sequences.append(int(suffix))
    exp_id = f"{prefix}{max(sequences, default=0) + 1:02d}"
    body = f"""# Experiment {exp_id}

- experiment_id: {exp_id}
- timestamp_utc: {now.strftime('%Y-%m-%dT%H:%M:%SZ')}
- operator:
- sport: {args.sport}
- hypothesis:
- target:
- grain:
- prediction_timestamp_rule:
- data_sources:
- data_snapshot:
- data_window:
- feature_set_ref:
- baseline_refs:
- validation_charter_ref:
- model_family:
- config_ref:
- random_seeds:
- metrics_primary:
- metrics_secondary:
- leakage_audit_status:
- results_summary:
- decision: keep | discard | follow-up
- next_actions:
- artifacts:
- commands:
- notes:
"""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{exp_id}.md"
    path.write_text(body, encoding="utf-8")
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
