"""Utility helpers for chronovault."""

from __future__ import annotations

import hashlib
import ipaddress
import secrets
import time
import uuid
from datetime import UTC, datetime
from typing import Any


def now_epoch() -> int:
    """Return current Unix epoch seconds as integer."""
    return int(time.time())


def now_iso() -> str:
    """Return current time in ISO 8601 UTC format."""
    return datetime.now(UTC).isoformat()


def uuid4_str() -> str:
    """Return random UUID4 string."""
    return str(uuid.uuid4())


def secure_token(length: int = 32) -> str:
    """Return URL-safe cryptographically secure token string."""
    return secrets.token_urlsafe(length)


def token_fingerprint(token: str) -> str:
    """Return SHA-256 token fingerprint for storage and comparisons."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def ensure_ip_allowed(source_ip: str, ip_allowlist: list[str]) -> bool:
    """Return True if source_ip matches any allowlist item or wildcard."""
    if not ip_allowlist:
        return False
    if "*" in ip_allowlist:
        return True

    try:
        ip_obj = ipaddress.ip_address(source_ip)
    except ValueError:
        return False

    for entry in ip_allowlist:
        try:
            if "/" in entry:
                if ip_obj in ipaddress.ip_network(entry, strict=False):
                    return True
            else:
                if ip_obj == ipaddress.ip_address(entry):
                    return True
        except ValueError:
            continue
    return False


def validate_ip_allowlist(ip_allowlist: list[str]) -> list[str]:
    """Validate and normalize IP/CIDR allowlist entries."""
    if not ip_allowlist:
        raise ValueError("ip_allowlist cannot be empty")

    normalized: list[str] = []
    for item in ip_allowlist:
        item = item.strip()
        if item == "*":
            normalized.append(item)
            continue
        if "/" in item:
            ipaddress.ip_network(item, strict=False)
            normalized.append(item)
        else:
            ipaddress.ip_address(item)
            normalized.append(item)
    return normalized


def redacted_error_message(err: Exception) -> str:
    """Return a safe generic error text without leaking internals."""
    _ = err
    return "operation failed"


def match_query(document: dict[str, Any], query: dict[str, Any]) -> bool:
    """Apply simple key/value, $gt and $in query matching to a document."""
    if not query:
        return True

    for key, expected in query.items():
        value = document.get(key)
        if isinstance(expected, dict):
            if "$gt" in expected:
                if value is None or value <= expected["$gt"]:
                    return False
            elif "$in" in expected:
                if value not in expected["$in"]:
                    return False
            else:
                return False
        else:
            if value != expected:
                return False
    return True
