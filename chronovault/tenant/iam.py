"""Role-based access control enforcement."""

from __future__ import annotations

from chronovault.exceptions import PermissionDeniedError


ROLE_ORDER = {
    "viewer": 1,
    "editor": 2,
    "admin": 3,
}

ACTION_MIN_ROLE = {
    "read": "viewer",
    "find": "viewer",
    "write": "editor",
    "update": "editor",
    "delete": "editor",
    "token.issue": "admin",
    "token.revoke": "admin",
    "audit.read": "admin",
    "rotate": "admin",
    "compliance": "admin",
}


class IAM:
    """Enforce RBAC role checks for ChronoVault actions."""

    @staticmethod
    def assert_allowed(role: str, action: str) -> None:
        """Raise when token role does not satisfy action minimum role."""
        role = role.lower()
        required = ACTION_MIN_ROLE.get(action)
        if required is None:
            return
        if ROLE_ORDER.get(role, 0) < ROLE_ORDER[required]:
            raise PermissionDeniedError("role is not allowed for this action")
