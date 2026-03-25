"""Encrypted migration tracking for collections."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any, Callable

from chronovault.exceptions import MigrationError
from chronovault.storage.store import JsonStore
from chronovault.utils import now_epoch, now_iso


class MigrationManager:
    """Track per-collection applied migration versions in encrypted JSON."""

    def __init__(
        self,
        store: JsonStore,
        file_path: Path,
        org_id: str,
        tenant_token: str,
        migrations_dir: Path | None = None,
        collection_factory: Callable[[str], Any] | None = None,
    ) -> None:
        self.store = store
        self.file_path = file_path
        self.org_id = org_id
        self.tenant_token = tenant_token
        self.migrations_dir = migrations_dir
        self.collection_factory = collection_factory

    @staticmethod
    def _parse_version(file_name: str) -> int | None:
        match = re.match(r"^v(\d+)", file_name)
        if not match:
            return None
        return int(match.group(1))

    def _discover_collection_migrations(self, collection: str) -> dict[int, Path]:
        if self.migrations_dir is None:
            return {}
        folder = self.migrations_dir / collection
        if not folder.exists() or not folder.is_dir():
            return {}

        discovered: dict[int, Path] = {}
        for path in sorted(folder.glob("v*.py")):
            version = self._parse_version(path.name)
            if version is None:
                continue
            discovered[version] = path
        return discovered

    def _load_module(self, path: Path) -> Any:
        module_name = f"chronovault_migration_{path.stem}_{abs(hash(path.as_posix()))}"
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        if spec is None or spec.loader is None:
            raise MigrationError("failed to load migration module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _run_migration(self, collection: str, direction: str, version: int, path: Path) -> None:
        if self.collection_factory is None:
            raise MigrationError("collection factory is required for migration execution")

        module = self._load_module(path)
        fn = getattr(module, direction, None)
        if not callable(fn):
            raise MigrationError(f"migration v{version} missing callable '{direction}'")

        coll = self.collection_factory(collection)
        records = coll.find({})
        migrated = fn(records)
        if not isinstance(migrated, list) or any(not isinstance(item, dict) for item in migrated):
            raise MigrationError("migration callable must return list[dict]")

        with coll._acquire_rw():
            coll._write_all(migrated)

    def _read_payload(self) -> dict[str, Any]:
        payload = self.store.read_encrypted_json(
            file_path=self.file_path,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
        )
        if not isinstance(payload.get("applied"), dict):
            payload["applied"] = {}
        return payload

    def _write_payload(self, payload: dict[str, Any]) -> None:
        payload["updated_at"] = now_iso()
        self.store.write_encrypted_json(
            file_path=self.file_path,
            payload=payload,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
            timestamp=now_epoch(),
            purpose="migrations",
        )

    def apply(self, collection: str, direction: str, version: int | None = None) -> dict[str, Any]:
        """Apply migration direction for one collection and return status payload."""
        payload = self._read_payload()
        applied = payload["applied"].get(collection, [])
        if not isinstance(applied, list):
            applied = []

        applied_versions = sorted({int(v) for v in applied})
        direction = direction.lower().strip()
        discovered = self._discover_collection_migrations(collection)

        if direction == "up":
            target = int(version) if version is not None else ((applied_versions[-1] + 1) if applied_versions else 1)
            if discovered and target not in discovered:
                raise MigrationError("migration file is not available for requested version")
            if target not in applied_versions:
                if target in discovered:
                    self._run_migration(collection=collection, direction="up", version=target, path=discovered[target])
                applied_versions.append(target)
                applied_versions.sort()
        elif direction == "down":
            if not applied_versions:
                raise MigrationError("no applied migrations for collection")
            target = int(version) if version is not None else int(applied_versions[-1])
            if target not in applied_versions:
                raise MigrationError("migration version is not applied")
            if discovered:
                if target not in discovered:
                    raise MigrationError("migration file is not available for requested version")
                self._run_migration(collection=collection, direction="down", version=target, path=discovered[target])
            applied_versions = [v for v in applied_versions if v != target]
        else:
            raise MigrationError("direction must be 'up' or 'down'")

        payload["applied"][collection] = applied_versions
        self._write_payload(payload)
        return {
            "collection": collection,
            "versions": applied_versions,
            "current": applied_versions[-1] if applied_versions else None,
        }

    def status(self) -> dict[str, Any]:
        """Return migration status for all collections."""
        payload = self._read_payload()
        result: dict[str, Any] = {"collections": {}}
        for collection, versions in payload.get("applied", {}).items():
            safe = sorted({int(v) for v in versions}) if isinstance(versions, list) else []
            result["collections"][collection] = {
                "versions": safe,
                "current": safe[-1] if safe else None,
            }
        return result
