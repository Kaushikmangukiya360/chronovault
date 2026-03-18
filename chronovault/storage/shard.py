"""Shard manager for encrypted collection data files."""

from __future__ import annotations

import re
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from chronovault.constants import CACHE_MAX_SHARDS, CACHE_TTL_SECONDS, MAX_QUERY_WORKERS, SHARD_SIZE
from chronovault.storage.store import JsonStore
from chronovault.utils import now_epoch


_SHARD_RE = re.compile(r"^data_(\d{3})\.json$")


class ShardManager:
    """Manage sharded encrypted collection records and read cache."""

    def __init__(self, store: JsonStore, collection_dir: Path, org_id: str, tenant_token: str) -> None:
        """Initialize shard manager for a collection directory."""
        self.store = store
        self.collection_dir = collection_dir
        self.org_id = org_id
        self.tenant_token = tenant_token
        self._cache: OrderedDict[str, tuple[float, list[dict[str, Any]]]] = OrderedDict()
        self._cache_lock = threading.Lock()

    def shard_path(self, shard_number: int) -> Path:
        """Return path for shard file number using data_###.json naming."""
        return self.collection_dir / f"data_{shard_number:03d}.json"

    def list_shards(self) -> list[Path]:
        """Return sorted shard file paths for collection."""
        if not self.collection_dir.exists():
            return []
        shards: list[tuple[int, Path]] = []
        for child in self.collection_dir.iterdir():
            if not child.is_file():
                continue
            m = _SHARD_RE.match(child.name)
            if m:
                shards.append((int(m.group(1)), child))
        shards.sort(key=lambda item: item[0])
        return [path for _, path in shards]

    def _cache_get(self, shard_path: Path) -> list[dict[str, Any]] | None:
        key = str(shard_path)
        with self._cache_lock:
            item = self._cache.get(key)
            if item is None:
                return None
            ts, records = item
            if time.time() - ts > CACHE_TTL_SECONDS:
                self._cache.pop(key, None)
                return None
            self._cache.move_to_end(key)
            return [dict(r) for r in records]

    def _cache_put(self, shard_path: Path, records: list[dict[str, Any]]) -> None:
        key = str(shard_path)
        with self._cache_lock:
            self._cache[key] = (time.time(), [dict(r) for r in records])
            self._cache.move_to_end(key)
            while len(self._cache) > CACHE_MAX_SHARDS:
                self._cache.popitem(last=False)

    def invalidate_cache(self, shard_path: Path | None = None) -> None:
        """Invalidate one shard cache entry or clear entire shard cache."""
        with self._cache_lock:
            if shard_path is None:
                self._cache.clear()
                return
            self._cache.pop(str(shard_path), None)

    def read_shard(self, shard_path: Path) -> list[dict[str, Any]]:
        """Read one shard records list from encrypted JSON payload."""
        cached = self._cache_get(shard_path)
        if cached is not None:
            return cached

        payload = self.store.read_encrypted_json(
            file_path=shard_path,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
        )
        records = payload.get("records", [])
        if not isinstance(records, list):
            records = []
        normalized = [r for r in records if isinstance(r, dict)]
        self._cache_put(shard_path, normalized)
        return [dict(r) for r in normalized]

    def read_all_records(self) -> list[dict[str, Any]]:
        """Read all records from all shards in parallel worker threads."""
        shards = self.list_shards()
        if not shards:
            return []

        with ThreadPoolExecutor(max_workers=MAX_QUERY_WORKERS) as pool:
            chunks = list(pool.map(self.read_shard, shards))

        all_records: list[dict[str, Any]] = []
        for chunk in chunks:
            all_records.extend(chunk)
        return all_records

    def write_records(self, records: list[dict[str, Any]]) -> tuple[int, int]:
        """Write all records across shards and return (shard_count, total_records)."""
        self.store.ensure_dir(self.collection_dir)
        current = self.list_shards()

        partitions: list[list[dict[str, Any]]] = []
        for idx in range(0, len(records), SHARD_SIZE):
            partitions.append(records[idx : idx + SHARD_SIZE])
        if not partitions:
            partitions = [[]]

        for i, part in enumerate(partitions):
            shard_path = self.shard_path(i)
            self.store.write_encrypted_json(
                file_path=shard_path,
                payload={"records": part, "shard": i, "total_shards": len(partitions)},
                tenant_token=self.tenant_token,
                org_id=self.org_id,
                timestamp=now_epoch(),
                purpose="data",
            )
            self.invalidate_cache(shard_path)

        keep = {p.name for p in [self.shard_path(i) for i in range(len(partitions))]}
        for path in current:
            if path.name not in keep:
                path.unlink(missing_ok=True)
                self.invalidate_cache(path)

        return len(partitions), len(records)
