"""Encrypted JSON file storage with file locking and atomic writes."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from filelock import FileLock, Timeout

from chronovault.constants import LOCK_TIMEOUT_SECONDS
from chronovault.core.cipher import decrypt_json_payload, encrypt_json_payload
from chronovault.exceptions import TamperDetectedError, VaultLockTimeoutError


class JsonStore:
    """Read/write encrypted JSON documents with lock-protected atomic writes."""

    def __init__(self, lock_timeout: int = 10) -> None:
        """Initialize a JSON store with lock timeout in seconds."""
        self.lock_timeout = lock_timeout if lock_timeout is not None else LOCK_TIMEOUT_SECONDS

    def ensure_dir(self, path: Path) -> None:
        """Create directory path with strict owner-only permissions."""
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(path, 0o700)

    def _lock_for(self, file_path: Path) -> FileLock:
        return FileLock(str(file_path) + ".lock")

    def _atomic_write_json(self, file_path: Path, data: dict[str, Any]) -> None:
        tmp_path = file_path.with_suffix(file_path.suffix + ".tmp")
        serialized = json.dumps(data, separators=(",", ":"), ensure_ascii=True)

        with open(tmp_path, "w", encoding="utf-8") as fh:
            fh.write(serialized)
        os.chmod(tmp_path, 0o600)
        os.replace(tmp_path, file_path)
        os.chmod(file_path, 0o600)

    def read_raw_json(self, file_path: Path) -> dict[str, Any]:
        """Read raw JSON dictionary from disk; empty dict if file is missing."""
        if not file_path.exists():
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                raise TamperDetectedError("JSON root must be an object")
            return data
        except json.JSONDecodeError as exc:
            raise TamperDetectedError("JSON decoding failed") from exc

    def write_raw_json(self, file_path: Path, data: dict[str, Any]) -> None:
        """Write raw JSON dictionary atomically with file lock."""
        self.ensure_dir(file_path.parent)
        lock = self._lock_for(file_path)
        try:
            with lock.acquire(timeout=self.lock_timeout):
                self._atomic_write_json(file_path=file_path, data=data)
        except Timeout as exc:
            raise VaultLockTimeoutError("failed to acquire file lock for write") from exc

    def read_encrypted_json(self, file_path: Path, tenant_token: str, org_id: str) -> dict[str, Any]:
        """Read encrypted JSON envelope and return decrypted object."""
        envelope = self.read_raw_json(file_path)
        if not envelope:
            return {}
        plaintext_json = decrypt_json_payload(envelope=envelope, tenant_token=tenant_token, org_id=org_id)
        try:
            payload = json.loads(plaintext_json)
        except json.JSONDecodeError as exc:
            raise TamperDetectedError("decrypted payload is not valid JSON") from exc
        if not isinstance(payload, dict):
            raise TamperDetectedError("decrypted JSON root must be an object")
        return payload

    def write_encrypted_json(
        self,
        file_path: Path,
        payload: dict[str, Any],
        tenant_token: str,
        org_id: str,
        timestamp: int,
        purpose: str = "data",
    ) -> None:
        """Encrypt and atomically write JSON payload with file lock."""
        self.ensure_dir(file_path.parent)
        lock = self._lock_for(file_path)
        envelope = encrypt_json_payload(
            payload_json=json.dumps(payload, separators=(",", ":"), ensure_ascii=True),
            tenant_token=tenant_token,
            org_id=org_id,
            timestamp=timestamp,
            purpose=purpose,
        )
        try:
            with lock.acquire(timeout=self.lock_timeout):
                self._atomic_write_json(file_path=file_path, data=envelope)
        except Timeout as exc:
            raise VaultLockTimeoutError("failed to acquire file lock for write") from exc
