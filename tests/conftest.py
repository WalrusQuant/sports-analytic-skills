"""Shared test configuration."""

from __future__ import annotations

import os


# Keep local and hosted test runs deterministic and avoid platform-specific
# physical-core detection warnings from joblib in sandboxed environments.
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")
