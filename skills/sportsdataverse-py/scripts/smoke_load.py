#!/usr/bin/env python3
"""Smoke test for sportsdataverse import and a lightweight module probe."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import pkgutil


def installed_version(package) -> str:
    try:
        return importlib.metadata.version("sportsdataverse")
    except importlib.metadata.PackageNotFoundError:
        return str(getattr(package, "__version__", "unknown"))


def discover_modules(package) -> list[str]:
    paths = getattr(package, "__path__", None)
    if paths is None:
        return []
    return sorted(
        item.name for item in pkgutil.iter_modules(paths)
        if not item.name.startswith("_")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--modules",
        default="nba,nfl,mlb,nhl,cfb,soccer",
        help="Comma-separated league modules to probe",
    )
    parser.add_argument("--list-modules", action="store_true")
    args = parser.parse_args()
    requested = [name.strip() for name in args.modules.split(",") if name.strip()]
    if not requested or any(not name.isidentifier() for name in requested):
        parser.error("--modules must contain comma-separated Python identifiers")
    try:
        import sportsdataverse
    except ImportError as exc:
        print(f"FAIL: sportsdataverse not installed ({exc})")
        print("Install: pip install sportsdataverse")
        return 1

    discovered = discover_modules(sportsdataverse)
    print(f"sportsdataverse import ok; version={installed_version(sportsdataverse)}")
    if args.list_modules:
        print("discovered public modules: " + (", ".join(discovered) or "none"))

    # Probe a few league namespaces without requiring a network-heavy pull.
    modules = []
    failed = []
    for name in requested:
        if discovered and name not in discovered:
            print(f"FAIL: sportsdataverse.{name} is not an installed module")
            failed.append(name)
            continue
        try:
            module = importlib.import_module(f"sportsdataverse.{name}")
            modules.append(name)
            public = [
                candidate for candidate in dir(module)
                if not candidate.startswith("_") and callable(getattr(module, candidate))
            ]
            print(f"OK: sportsdataverse.{name} imported; public_callables={len(public)}")
        except Exception as exc:  # module layout can vary by version
            print(f"FAIL: sportsdataverse.{name} unavailable: {exc}")
            failed.append(name)

    if not modules:
        print("FAIL: no league modules imported")
        return 2
    if failed:
        print(f"FAIL: partial probe; imported={','.join(modules)} failed={','.join(failed)}")
        return 3

    print(f"OK: all requested league modules importable: {', '.join(modules)}")
    print("Note: endpoint calls are version-specific; use package docs for live pulls.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
