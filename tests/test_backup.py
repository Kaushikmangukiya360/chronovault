import chronovault as cv
from chronovault.exceptions import RestoreError


def test_backup_and_restore_force(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-backup", path=str(tmp_path))
    db.users.insert({"name": "Alice", "age": 30})

    backup_path = tmp_path / "backup_org_backup.json"
    db.backup(output_path=str(backup_path), include_audit=True)
    assert backup_path.exists()

    with db.transaction() as tx:
        tx.users.insert({"name": "Bob", "age": 25})
    assert db.users.count() == 2

    # Without force, restore should refuse overwrite.
    try:
        db.restore(input_path=str(backup_path), force=False)
        assert False
    except RestoreError:
        pass

    db.restore(input_path=str(backup_path), force=True)
    rows = db.users.find({})
    assert len(rows) == 1
    assert rows[0]["name"] == "Alice"
