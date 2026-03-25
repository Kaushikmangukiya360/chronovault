"""Encrypted tenant backup and restore manager."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from chronovault.exceptions import BackupError, RestoreError
from chronovault.storage.store import JsonStore
from chronovault.utils import now_epoch, now_iso


class BackupManager:
    """Export and restore tenant data using encrypted backup snapshots."""

    def __init__(self, store: JsonStore, tenant_root: Path, org_id: str, tenant_token: str) -> None:
        self.store = store
        self.tenant_root = tenant_root
        self.org_id = org_id
        self.tenant_token = tenant_token

    def _collect_json_files(self) -> dict[str, dict[str, Any]]:
        files: dict[str, dict[str, Any]] = {}
        if not self.tenant_root.exists():
            return files

        for path in sorted(self.tenant_root.rglob("*.json")):
            rel = path.relative_to(self.tenant_root).as_posix()
            files[rel] = self.store.read_raw_json(path)
        return files

    def export(self, output_path: str, include_audit: bool = True) -> None:
        """Export tenant files into one encrypted backup file."""
        try:
            files = self._collect_json_files()
            if not include_audit:
                files.pop("audit.json", None)

            payload = {
                "org_id": self.org_id,
                "created_at": now_iso(),
                "include_audit": bool(include_audit),
                "files": files,
            }
            self.store.write_encrypted_json(
                file_path=Path(output_path),
                payload=payload,
                tenant_token=self.tenant_token,
                org_id=self.org_id,
                timestamp=now_epoch(),
                purpose="backup",
            )
        except Exception as exc:  # noqa: BLE001
            raise BackupError("backup export failed") from exc

    def restore(self, input_path: str, force: bool = False) -> None:
        """Restore tenant files from one encrypted backup file."""
        try:
            payload = self.store.read_encrypted_json(
                file_path=Path(input_path),
                tenant_token=self.tenant_token,
                org_id=self.org_id,
            )
        except Exception as exc:  # noqa: BLE001
            raise RestoreError("backup read failed") from exc

        backup_org = str(payload.get("org_id", ""))
        if backup_org != self.org_id:
            raise RestoreError("backup org mismatch")

        files = payload.get("files", {})
        if not isinstance(files, dict):
            raise RestoreError("backup payload is invalid")

        existing_files = list(self.tenant_root.rglob("*.json")) if self.tenant_root.exists() else []
        if existing_files and not force:
            raise RestoreError("refusing to overwrite existing tenant data without force")

        self.store.ensure_dir(self.tenant_root)
        for rel, data in files.items():
            if not isinstance(rel, str) or not isinstance(data, dict):
                continue
            target = self.tenant_root / rel
            self.store.write_raw_json(target, data)
