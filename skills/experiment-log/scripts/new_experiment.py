#!/usr/bin/env python3
"""Create a new experiment log markdown stub with a timestamped ID."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--slug", default="run")
    p.add_argument("--sport", default="")
    p.add_argument("--out-dir", default="data/experiments")
    args = p.parse_args()

    now = datetime.now(timezone.utc)
    exp_id = f"{now.strftime('%Y%m%d')}-{args.slug}-01"
    body = f"""# Experiment {exp_id}

- experiment_id: {exp_id}
- timestamp_utc: {now.strftime('%Y-%m-%dT%H:%M:%SZ')}
- operator:
- sport: {args.sport}
- hypothesis:
- target:
- prediction_timestamp_rule:
- data_sources:
- data_window:
- feature_set_ref:
- baseline_refs:
- validation_charter_ref:
- model_family:
- config_ref:
- metrics_primary:
- metrics_secondary:
- leakage_audit_status:
- results_summary:
- decision: keep | discard | follow-up
- next_actions:
- artifacts:
- package_commands:
- notes:
"""
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{exp_id}.md"
    path.write_text(body, encoding="utf-8")
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
