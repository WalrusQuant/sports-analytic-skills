#!/usr/bin/env python3
"""Smoke test for sportsdataverse import and a lightweight module probe."""

from __future__ import annotations


def main() -> int:
    try:
        import sportsdataverse  # noqa: F401
    except ImportError as exc:
        print(f"FAIL: sportsdataverse not installed ({exc})")
        print("Install: pip install sportsdataverse")
        return 1

    print("sportsdataverse import ok")

    # Probe a few league namespaces without requiring a network-heavy pull.
    modules = []
    for name in ("nba", "nfl", "mlb", "nhl", "cfb", "soccer"):
        try:
            __import__(f"sportsdataverse.{name}")
            modules.append(name)
        except Exception as exc:  # module layout can vary by version
            print(f"WARN: sportsdataverse.{name} unavailable: {exc}")

    if not modules:
        print("FAIL: no league modules imported")
        return 2

    print(f"OK: league modules importable: {', '.join(modules)}")
    print("Note: endpoint calls are version-specific; use package docs for live pulls.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
