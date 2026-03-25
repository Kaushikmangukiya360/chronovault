import chronovault as cv
from chronovault.exceptions import MigrationError


def test_migration_up_down_status(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-migrate", path=str(tmp_path))

    up1 = db.migrate(collection="users", direction="up")
    assert up1["current"] == 1

    up2 = db.migrate(collection="users", direction="up")
    assert up2["current"] == 2

    up_idempotent = db.migrate(collection="users", direction="up", version=2)
    assert up_idempotent["versions"] == [1, 2]

    status = db.migration_status()
    assert status["collections"]["users"]["current"] == 2

    down = db.migrate(collection="users", direction="down", version=2)
    assert down["current"] == 1


def test_migration_down_missing_raises(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-migrate-2", path=str(tmp_path))

    try:
        db.migrate(collection="users", direction="down")
        assert False
    except MigrationError:
        pass


def test_migration_executes_file_up_down(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-migrate-files", path=str(tmp_path))
    db.users.insert({"name": "alice", "age": 30})

    migrations_dir = tmp_path / "tenants" / "org-migrate-files" / "migrations" / "users"
    migrations_dir.mkdir(parents=True, exist_ok=True)
    (migrations_dir / "v1_add_status.py").write_text(
        """
def up(records):
    for item in records:
        item["status"] = "active"
    return records

def down(records):
    for item in records:
        item.pop("status", None)
    return records
""".strip()
        + "\n",
        encoding="utf-8",
    )

    up = db.migrate(collection="users", direction="up", version=1)
    assert up["current"] == 1
    assert db.users.find_one({"name": "alice"})["status"] == "active"

    down = db.migrate(collection="users", direction="down", version=1)
    assert down["current"] is None
    assert "status" not in db.users.find_one({"name": "alice"})


def test_migration_file_invalid_return_raises(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-migrate-invalid", path=str(tmp_path))
    db.users.insert({"name": "alice"})

    migrations_dir = tmp_path / "tenants" / "org-migrate-invalid" / "migrations" / "users"
    migrations_dir.mkdir(parents=True, exist_ok=True)
    (migrations_dir / "v1_bad.py").write_text(
        """
def up(records):
    return {"invalid": True}

def down(records):
    return records
""".strip()
        + "\n",
        encoding="utf-8",
    )

    try:
        db.migrate(collection="users", direction="up", version=1)
        assert False
    except MigrationError:
        pass
