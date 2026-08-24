#!/usr/bin/env python3
"""Verify a Python analysis environment without depending on a project package."""

from __future__ import annotations

import argparse
import importlib
import json
import platform
import sys
from pathlib import Path


DEFAULT_PACKAGES = ("numpy", "pandas", "sklearn")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--packages",
        default=",".join(DEFAULT_PACKAGES),
        help="Comma-separated import names to verify",
    )
    parser.add_argument("--out", default="", help="Optional JSON report path")
    args = parser.parse_args()

    packages = [name.strip() for name in args.packages.split(",") if name.strip()]
    if not packages:
        parser.error("--packages must contain at least one import name")
    invalid = [
        name for name in packages if not all(part.isidentifier() for part in name.split("."))
    ]
    if invalid:
        parser.error(f"invalid import names: {', '.join(invalid)}")
    out = Path(args.out) if args.out else None
    if out is not None and out.suffix.lower() != ".json":
        parser.error("--out must end in .json")

    checked: list[dict[str, str | bool]] = []
    failed = False
    for name in packages:
        try:
            module = importlib.import_module(name)
            version = str(getattr(module, "__version__", "unknown"))
            checked.append({"package": name, "available": True, "version": version})
        except Exception as exc:  # import errors can include missing native libraries
            failed = True
            checked.append({"package": name, "available": False, "error": str(exc)})

    report = {
        "python": platform.python_version(),
        "executable": sys.executable,
        "platform": platform.platform(),
        "packages": checked,
        "status": "FAIL" if failed else "OK",
    }
    print(json.dumps(report, indent=2))

    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
