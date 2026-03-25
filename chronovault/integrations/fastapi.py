"""FastAPI integration helpers for ChronoVault."""

from __future__ import annotations

from typing import Any, Callable

import chronovault as cv


def CVDepends(token: str, org: str, path: str = "~/.chronovault") -> Callable[[], Any]:
    """Return a FastAPI dependency that yields a ChronoVault connection."""

    def _dependency() -> Any:
        return cv.connect(token=token, org_id=org, path=path)

    return _dependency
