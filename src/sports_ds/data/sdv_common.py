"""Shared SportsDataverse loader utilities."""

from __future__ import annotations

import importlib
from typing import Any, Callable


class MultiSportDataError(RuntimeError):
    """Raised when optional multi-sport data cannot be loaded."""


def require_sportsdataverse() -> None:
    try:
        import sportsdataverse  # noqa: F401
    except ImportError as exc:
        raise MultiSportDataError(
            'sportsdataverse is required. Install with: pip install -e ".[multi]"'
        ) from exc


def try_call_loaders(candidates: list[tuple[str, str]], call_args: list[dict[str, Any]]) -> Any:
    """Try module.function candidates with multiple kw/pos calling conventions."""
    last_err: Exception | None = None
    for mod_name, fn_name in candidates:
        try:
            mod = importlib.import_module(mod_name)
            fn: Callable = getattr(mod, fn_name)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            continue
        for kwargs in call_args:
            try:
                return fn(**kwargs)
            except TypeError:
                # positional fallbacks for single-arg loaders
                vals = list(kwargs.values())
                try:
                    if len(vals) == 1:
                        return fn(vals[0])
                    return fn(*vals)
                except Exception as exc:  # noqa: BLE001
                    last_err = exc
                    continue
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                continue
    raise MultiSportDataError(f"no loader succeeded; last_error={last_err}")
