import pytest

import chronovault as cv
from chronovault.exceptions import TransactionConflictError


def test_transaction_commit(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-tx-commit", path=str(tmp_path))

    with db.transaction() as tx:
        tx.users.insert({"name": "Alice", "age": 30})
        tx.users.insert({"name": "Bob", "age": 25})
        tx.users.update({"name": "Bob"}, {"age": 26})

    rows = db.users.find({})
    assert len(rows) == 2
    assert db.users.find_one({"name": "Bob"})["age"] == 26
    assert db.health_check()["pending_wal"] == 0


def test_transaction_rollback(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-tx-rollback", path=str(tmp_path))

    with pytest.raises(RuntimeError):
        with db.transaction() as tx:
            tx.users.insert({"name": "Alice", "age": 30})
            raise RuntimeError("force rollback")

    assert db.users.count() == 0
    assert db.health_check()["pending_wal"] == 0


def test_transaction_conflict_pending(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-tx-conflict", path=str(tmp_path))

    tx1 = db.transaction()
    with tx1:
        tx1.users.insert({"name": "Alice", "age": 30})
        with pytest.raises(TransactionConflictError):
            _ = db.transaction().__enter__()
