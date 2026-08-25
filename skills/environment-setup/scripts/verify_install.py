#!/usr/bin/env python3
"""Verify a Python analysis environment without depending on a project package."""

from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import json
import platform
import subprocess
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
        import_stdout = io.StringIO()
        import_stderr = io.StringIO()
        try:
            with contextlib.redirect_stdout(import_stdout), contextlib.redirect_stderr(
                import_stderr
            ):
                module = importlib.import_module(name)
            version = str(getattr(module, "__version__", "unknown"))
            item = {"package": name, "available": True, "version": version}
        except Exception as exc:  # import errors can include missing native libraries
            failed = True
            item = {"package": name, "available": False, "error": str(exc)}
        if import_stdout.getvalue():
            item["import_stdout"] = import_stdout.getvalue()
        if import_stderr.getvalue():
            item["import_stderr"] = import_stderr.getvalue()
        checked.append(item)

    try:
        pip_probe = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        pip_available = pip_probe.returncode == 0
        pip_detail = (pip_probe.stdout if pip_available else pip_probe.stderr).strip()
    except (OSError, subprocess.SubprocessError) as exc:
        pip_available = False
        pip_detail = str(exc)
    failed = failed or not pip_available

    report = {
        "python": platform.python_version(),
        "executable": sys.executable,
        "platform": platform.platform(),
        "prefix": sys.prefix,
        "base_prefix": sys.base_prefix,
        "standard_venv_detected": sys.prefix != sys.base_prefix,
        "pip": {"available": pip_available, "detail": pip_detail},
        "requested_imports": packages,
        "packages": checked,
        "status": "FAIL" if failed else "OK",
        "checks_not_run": [
            "helper_help",
            "file_round_trips",
            "loader_network_sample",
            "lock_recreation",
        ],
        "limitations": (
            "OK covers this interpreter, python -m pip, and requested imports only; "
            "standard_venv_detected does not recognize every environment manager."
        ),
    }
    text = json.dumps(report, indent=2)

    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    # Stdout is always exactly one JSON document, including when --out is used.
    print(text)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
