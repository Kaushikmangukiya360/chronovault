import time

import chronovault as cv


def test_rotate_key_changes_epoch(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-rot", path=str(tmp_path))
    db.users.insert({"name": "A"})

    path = db._tenant_root / "collections" / "users" / "data_000.json"
    before = db._store.read_raw_json(path)["ts"]

    time.sleep(1.1)
    db.users.rotate_key()

    after = db._store.read_raw_json(path)["ts"]
    assert after > before
