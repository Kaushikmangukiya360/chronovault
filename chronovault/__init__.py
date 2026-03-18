"""Public API for chronovault package."""

from __future__ import annotations

from chronovault.core.vault import ChronoVault


def connect(
    token: str,
    org_id: str,
    path: str,
    role: str = "admin",
    ip_allowlist: list[str] | None = None,
    tls: bool = False,
) -> ChronoVault:
    """Connect to or initialize a ChronoVault tenant."""
    return ChronoVault(
        token=token,
        org_id=org_id,
        path=path,
        role=role,
        ip_allowlist=ip_allowlist,
        tls=tls,
    )


__all__ = ["connect", "ChronoVault"]
