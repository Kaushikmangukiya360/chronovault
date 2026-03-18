"""Simple local test script for chronovault.

Run with:
    python example.py

This script initializes a tenant workspace in a temporary directory,
creates a test collection, inserts a document, reads it back, and prints
some basic status information.
"""

from __future__ import annotations

import json
import tempfile
import uuid

import chronovault


def main() -> None:
    org_id = "local-org"
    token = "local-token"

    # Use a temporary directory so repeated runs are clean.
    with tempfile.TemporaryDirectory(prefix="chronovault-") as tmpdir:
        print("Using workspace:", tmpdir)

        db = chronovault.connect(org_id=org_id, token=token, path=tmpdir)

        # Tenant metadata
        info = db.tenant_info()
        print("Tenant info:", json.dumps(info, indent=2))

        # Collection operations
        coll = db.test_collection
        print("Collection name:", coll.name)

        rec_id = coll.insert({"name": "Alice", "age": 30})
        print("Inserted record id:", rec_id)

        found = coll.find_one({"name": "Alice"})
        print("Found record:", json.dumps(found, indent=2))

        count = coll.count({})
        print("Document count:", count)

        # Audit log (requires a tenant with role permissions)
        logs = db.audit_log.tail(n=5)
        print("Recent audit entries:", json.dumps(logs, indent=2))


if __name__ == "__main__":
    main()
