"""Key rotation logic for collection and tenant-wide re-encryption."""

from __future__ import annotations

from pathlib import Path

from chronovault.storage.collection import Collection
from chronovault.storage.store import JsonStore
from chronovault.utils import now_epoch, now_iso


class Rekeyer:
    """Rotate collection encryption by re-writing payloads at a new epoch."""

    def __init__(self, store: JsonStore, tenant_root: Path, org_id: str, tenant_token: str) -> None:
        """Initialize rekeyer for one tenant scope."""
        self.store = store
        self.tenant_root = tenant_root
        self.org_id = org_id
        self.tenant_token = tenant_token

    def rotate_collection(self, collection: str) -> None:
        """Rotate one collection key epoch by re-encrypting all records."""
        coll = Collection(
            store=self.store,
            tenant_root=self.tenant_root,
            org_id=self.org_id,
            tenant_token=self.tenant_token,
            name=collection,
        )
        coll.rotate_key()
        self._append_key_meta(event="collection.rotate", collection=collection)

    def rotate_all(self) -> None:
        """Rotate all tenant collections and append key metadata events."""
        collections_root = self.tenant_root / "collections"
        if not collections_root.exists():
            return

        for child in collections_root.iterdir():
            if not child.is_dir():
                continue
            self.rotate_collection(collection=child.name)

    def _append_key_meta(self, event: str, collection: str) -> None:
        keys_path = self.tenant_root / "keys_meta.json"
        payload = self.store.read_encrypted_json(
            file_path=keys_path,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
        )
        history = payload.get("history", [])
        if not isinstance(history, list):
            history = []
        history.append(
            {
                "event": event,
                "collection": collection,
                "epoch": now_epoch(),
                "at": now_iso(),
            }
        )
        payload["history"] = history
        self.store.write_encrypted_json(
            file_path=keys_path,
            payload=payload,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
            timestamp=now_epoch(),
            purpose="keys_meta",
        )
