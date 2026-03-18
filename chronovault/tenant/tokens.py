"""Token issuance, validation, TTL, revocation, and IP binding."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from chronovault.exceptions import AuthenticationError, InvalidTokenError, TokenExpiredError, TokenRevokedError, UnauthorizedIPError
from chronovault.storage.store import JsonStore
from chronovault.utils import ensure_ip_allowed, now_epoch, now_iso, secure_token, token_fingerprint, validate_ip_allowlist


class TokenService:
    """Manage encrypted tenant token registry and token checks."""

    def __init__(self, store: JsonStore, tokens_path: Path, org_id: str, tenant_token: str) -> None:
        """Initialize token service with tenant context."""
        self.store = store
        self.tokens_path = tokens_path
        self.org_id = org_id
        self.tenant_token = tenant_token

    def _read_payload(self) -> dict[str, Any]:
        payload = self.store.read_encrypted_json(
            file_path=self.tokens_path,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
        )
        if "tokens" not in payload:
            payload["tokens"] = []
        return payload

    def _write_payload(self, payload: dict[str, Any]) -> None:
        self.store.write_encrypted_json(
            file_path=self.tokens_path,
            payload=payload,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
            timestamp=now_epoch(),
            purpose="tokens",
        )

    def issue_token(
        self,
        name: str,
        role: str,
        collections: list[str] | None = None,
        ip_allowlist: list[str] | None = None,
        ttl: int | None = None,
        single_use: bool = False,
    ) -> str:
        """Issue a token and return the secret once."""
        role = role.lower()
        if role not in {"admin", "editor", "viewer"}:
            raise InvalidTokenError("invalid role")

        allowlist = validate_ip_allowlist(ip_allowlist or ["*"])
        payload = self._read_payload()
        tokens = payload.get("tokens", [])

        tokens = [t for t in tokens if t.get("name") != name]
        secret = secure_token(32)
        token_hash = token_fingerprint(secret)
        issued = now_iso()
        expires_at = int(time.time()) + ttl if ttl is not None else None

        tokens.append(
            {
                "name": name,
                "token_hash": token_hash,
                "role": role,
                "collections": collections or ["*"],
                "ip_allowlist": allowlist,
                "issued_at": issued,
                "expires_at": expires_at,
                "revoked": False,
                "single_use": bool(single_use),
                "used": False,
            }
        )

        payload["tokens"] = tokens
        self._write_payload(payload)
        return secret

    def revoke_token(self, name: str) -> None:
        """Revoke token by name."""
        payload = self._read_payload()
        for token in payload.get("tokens", []):
            if token.get("name") == name:
                token["revoked"] = True
        self._write_payload(payload)

    def list_tokens(self) -> list[dict[str, Any]]:
        """List token metadata excluding token hashes."""
        payload = self._read_payload()
        result: list[dict[str, Any]] = []
        for token in payload.get("tokens", []):
            result.append(
                {
                    "name": token.get("name"),
                    "role": token.get("role"),
                    "collections": token.get("collections", []),
                    "ip_allowlist": token.get("ip_allowlist", []),
                    "issued_at": token.get("issued_at"),
                    "expires_at": token.get("expires_at"),
                    "revoked": token.get("revoked", False),
                    "single_use": token.get("single_use", False),
                    "used": token.get("used", False),
                }
            )
        return result

    def validate(self, token: str, source_ip: str, collection: str | None = None) -> dict[str, Any]:
        """Validate token against hash, revocation, TTL, single-use, and IP binding."""
        payload = self._read_payload()
        token_hash = token_fingerprint(token)

        matched: dict[str, Any] | None = None
        for item in payload.get("tokens", []):
            if item.get("token_hash") == token_hash:
                matched = item
                break

        if matched is None:
            raise AuthenticationError("token authentication failed")
        if matched.get("revoked"):
            raise TokenRevokedError("token is revoked")

        expires_at = matched.get("expires_at")
        if expires_at is not None and int(time.time()) >= int(expires_at):
            raise TokenExpiredError("token expired")

        if matched.get("single_use") and matched.get("used"):
            raise TokenExpiredError("single-use token already consumed")

        allowlist = matched.get("ip_allowlist", ["*"])
        if not ensure_ip_allowed(source_ip=source_ip, ip_allowlist=allowlist):
            raise UnauthorizedIPError("source IP is not allowed")

        allowed_collections = matched.get("collections", ["*"])
        if collection is not None and "*" not in allowed_collections and collection not in allowed_collections:
            raise UnauthorizedIPError("token collection scope does not allow requested collection")

        return {
            "name": matched.get("name"),
            "role": matched.get("role"),
            "collections": allowed_collections,
            "single_use": bool(matched.get("single_use", False)),
            "used": bool(matched.get("used", False)),
        }

    def mark_used(self, token: str) -> None:
        """Mark a single-use token as consumed."""
        payload = self._read_payload()
        token_hash = token_fingerprint(token)
        changed = False

        for item in payload.get("tokens", []):
            if item.get("token_hash") == token_hash and item.get("single_use"):
                item["used"] = True
                changed = True

        if changed:
            self._write_payload(payload)
