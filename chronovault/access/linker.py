"""HMAC-signed, time-limited access link generation and validation."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from pathlib import Path
from typing import Any

from chronovault.exceptions import TokenExpiredError
from chronovault.storage.store import JsonStore
from chronovault.utils import now_epoch, uuid4_str


class Linker:
    """Issue and validate HMAC-SHA256 signed access links."""

    def __init__(
        self,
        store: JsonStore,
        tokens_path: Path,
        org_id: str,
        tenant_token: str,
        base_url: str = "http://127.0.0.1:8471",
    ) -> None:
        """Initialize linker with token registry path and tenant context."""
        self.store = store
        self.tokens_path = tokens_path
        self.org_id = org_id
        self.tenant_token = tenant_token
        self.base_url = base_url.rstrip("/")

    def _b64url_encode(self, raw: bytes) -> str:
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    def _b64url_decode(self, value: str) -> bytes:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode((value + padding).encode("ascii"))

    def _sign(self, message: str) -> str:
        digest = hmac.new(
            key=self.tenant_token.encode("utf-8"),
            msg=message.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        return digest

    def generate_link(
        self,
        collection: str,
        ttl: int,
        ip: str,
        permissions: list[str],
        single_use: bool = True,
    ) -> str:
        """Generate signed access URL token with optional single-use semantics."""
        expiry = int(time.time()) + int(ttl)
        jti = uuid4_str()
        perms = ",".join(sorted(permissions))
        message = f"{self.org_id}|{collection}|{expiry}|{ip}|{perms}|{jti}|{int(single_use)}"
        signature = self._sign(message)

        payload = {
            "org_id": self.org_id,
            "collection": collection,
            "exp": expiry,
            "ip": ip,
            "permissions": permissions,
            "single_use": bool(single_use),
            "jti": jti,
            "sig": signature,
        }
        token = self._b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

        if single_use:
            raw = self.store.read_encrypted_json(
                file_path=self.tokens_path,
                tenant_token=self.tenant_token,
                org_id=self.org_id,
            )
            used = raw.get("used_links", {})
            if not isinstance(used, dict):
                used = {}
            used[jti] = False
            raw["used_links"] = used
            self.store.write_encrypted_json(
                file_path=self.tokens_path,
                payload=raw,
                tenant_token=self.tenant_token,
                org_id=self.org_id,
                timestamp=now_epoch(),
                purpose="tokens",
            )

        return f"{self.base_url}/access?t={token}"

    def validate_token(self, token: str, source_ip: str) -> dict[str, Any]:
        """Validate signature, expiry, source IP, and single-use state."""
        try:
            payload = json.loads(self._b64url_decode(token).decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            raise TokenExpiredError("invalid access link") from exc

        required = {"org_id", "collection", "exp", "ip", "permissions", "single_use", "jti", "sig"}
        if not required.issubset(payload.keys()):
            raise TokenExpiredError("invalid access link")

        if int(time.time()) >= int(payload["exp"]):
            raise TokenExpiredError("access link expired")

        if payload["ip"] != "*" and payload["ip"] != source_ip:
            raise TokenExpiredError("access link IP mismatch")

        perms = ",".join(sorted(payload.get("permissions", [])))
        message = (
            f"{payload['org_id']}|{payload['collection']}|{int(payload['exp'])}|{payload['ip']}|"
            f"{perms}|{payload['jti']}|{int(bool(payload['single_use']))}"
        )
        expected_sig = self._sign(message)
        if not hmac.compare_digest(expected_sig, str(payload["sig"])):
            raise TokenExpiredError("access link signature mismatch")

        if payload["single_use"]:
            raw = self.store.read_encrypted_json(
                file_path=self.tokens_path,
                tenant_token=self.tenant_token,
                org_id=self.org_id,
            )
            used = raw.get("used_links", {})
            if used.get(payload["jti"], False):
                raise TokenExpiredError("single-use access link already used")
            used[payload["jti"]] = True
            raw["used_links"] = used
            self.store.write_encrypted_json(
                file_path=self.tokens_path,
                payload=raw,
                tenant_token=self.tenant_token,
                org_id=self.org_id,
                timestamp=now_epoch(),
                purpose="tokens",
            )

        return payload
