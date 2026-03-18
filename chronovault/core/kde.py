"""Key Derivation Engine (HKDF-SHA256) for time-keyed encryption."""

from __future__ import annotations

import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def derive_key(tenant_token: str, org_id: str, timestamp: int | None = None) -> bytes:
    """Derive a 32-byte AES key using HKDF-SHA256 from token, org, and epoch."""
    ts = int(time.time()) if timestamp is None else int(timestamp)
    ikm = f"{org_id}:{tenant_token}".encode("utf-8")
    salt = ts.to_bytes(8, "big", signed=False)
    info = f"chronovault-v1:{org_id}:{ts}".encode("utf-8")
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=info,
        backend=default_backend(),
    )
    return hkdf.derive(ikm)
