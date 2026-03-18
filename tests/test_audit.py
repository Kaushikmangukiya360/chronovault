import pytest

import chronovault as cv
from chronovault.exceptions import AuditIntegrityError
from chronovault.utils import now_epoch


def test_audit_append_verify_export(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-audit", path=str(tmp_path))

    db._audit.append("collection.write", "token:test", "users", None, "127.0.0.1", "success")
    db._audit.append("collection.read", "token:test", "users", None, "127.0.0.1", "success")

    assert db.audit_log.verify_integrity() is True

    out = tmp_path / "audit_export.json"
    db.audit_log.export(str(out))
    assert out.exists()

    audit_path = db._tenant_root / "audit.json"
    payload = db._store.read_encrypted_json(audit_path, db.token, db.org_id)
    payload["entries"][1]["prev_hash"] = "bad"
    db._store.write_encrypted_json(audit_path, payload, db.token, db.org_id, now_epoch(), purpose="audit")

    with pytest.raises(AuditIntegrityError):
        db.audit_log.verify_integrity()
