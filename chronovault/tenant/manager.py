"""Tenant provisioning and metadata management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from chronovault.exceptions import TenantAlreadyExistsError, TenantNotFoundError
from chronovault.storage.store import JsonStore
from chronovault.utils import now_epoch, now_iso, token_fingerprint, validate_ip_allowlist


class TenantManager:
    """Provision tenant directories and foundational encrypted files."""

    def __init__(self, store: JsonStore, base_path: Path) -> None:
        """Initialize tenant manager with base ChronoVault path."""
        self.store = store
        self.base_path = Path(base_path).expanduser()
        self.tenants_dir = self.base_path / "tenants"
        self.store.ensure_dir(self.tenants_dir)

    def tenant_root(self, org_id: str) -> Path:
        """Return tenant root path for org_id."""
        return self.tenants_dir / org_id

    def exists(self, org_id: str) -> bool:
        """Return True if tenant config exists."""
        return (self.tenant_root(org_id) / "config.json").exists()

    def create(
        self,
        org_id: str,
        tenant_token: str,
        role: str = "admin",
        ip_allowlist: list[str] | None = None,
        tls: bool = False,
    ) -> Path:
        """Create a new tenant with initial admin token metadata."""
        if self.exists(org_id):
            raise TenantAlreadyExistsError("tenant already exists")

        root = self.tenant_root(org_id)
        self.store.ensure_dir(root)
        self.store.ensure_dir(root / "collections")

        allowlist = validate_ip_allowlist(ip_allowlist or ["*"])
        now = now_iso()
        ts = now_epoch()

        self.store.write_encrypted_json(
            file_path=root / "config.json",
            payload={
                "org_id": org_id,
                "created_at": now,
                "tls": bool(tls),
                "schema": 1,
            },
            tenant_token=tenant_token,
            org_id=org_id,
            timestamp=ts,
            purpose="config",
        )

        self.store.write_encrypted_json(
            file_path=root / "tokens.json",
            payload={
                "tokens": [
                    {
                        "name": "root",
                        "token_hash": token_fingerprint(tenant_token),
                        "role": role.lower(),
                        "collections": ["*"],
                        "ip_allowlist": allowlist,
                        "issued_at": now,
                        "expires_at": None,
                        "revoked": False,
                        "single_use": False,
                        "used": False,
                    }
                ]
            },
            tenant_token=tenant_token,
            org_id=org_id,
            timestamp=ts,
            purpose="tokens",
        )

        self.store.write_encrypted_json(
            file_path=root / "audit.json",
            payload={"entries": []},
            tenant_token=tenant_token,
            org_id=org_id,
            timestamp=ts,
            purpose="audit",
        )

        self.store.write_encrypted_json(
            file_path=root / "keys_meta.json",
            payload={"history": [{"event": "tenant.create", "epoch": ts, "at": now}]},
            tenant_token=tenant_token,
            org_id=org_id,
            timestamp=ts,
            purpose="keys_meta",
        )
        return root

    def ensure(
        self,
        org_id: str,
        tenant_token: str,
        role: str = "admin",
        ip_allowlist: list[str] | None = None,
        tls: bool = False,
    ) -> Path:
        """Create tenant if missing and return root path."""
        if not self.exists(org_id):
            return self.create(
                org_id=org_id,
                tenant_token=tenant_token,
                role=role,
                ip_allowlist=ip_allowlist,
                tls=tls,
            )
        return self.tenant_root(org_id)

    def tenant_info(self, org_id: str, tenant_token: str) -> dict[str, Any]:
        """Return non-secret tenant metadata from config."""
        config_path = self.tenant_root(org_id) / "config.json"
        if not config_path.exists():
            raise TenantNotFoundError("tenant not found")
        payload = self.store.read_encrypted_json(
            file_path=config_path,
            tenant_token=tenant_token,
            org_id=org_id,
        )
        return {
            "org_id": payload.get("org_id"),
            "created_at": payload.get("created_at"),
            "tls": payload.get("tls"),
            "schema": payload.get("schema", 1),
        }
