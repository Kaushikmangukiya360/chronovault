import chronovault as cv
import pytest

from chronovault.exceptions import PermissionDeniedError


def test_inner_left_right_join(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-join", path=str(tmp_path))
    u1 = db.users.insert({"name": "Alice"})
    _u2 = db.users.insert({"name": "Bob"})
    db.orders.insert_many(
        [
            {"user_id": u1, "amount": 100, "status": "paid"},
            {"user_id": "missing", "amount": 200, "status": "paid"},
        ]
    )

    inner = db.orders.find({}).join("users", on="user_id", foreign_key="_id", join_type="inner").execute()
    assert len(inner) == 1
    assert inner[0]["users"]["name"] == "Alice"

    left = db.orders.find({}).join("users", on="user_id", foreign_key="_id", join_type="left").execute()
    assert len(left) == 2
    assert any(r["users"] is None for r in left)

    right = db.orders.find({}).join("users", on="user_id", foreign_key="_id", join_type="right").execute()
    assert len(right) >= 2


def test_join_disallows_unscoped_collection_access(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-join-rbac", path=str(tmp_path))
    u1 = db.users.insert({"name": "Alice"})
    db.orders.insert({"user_id": u1, "amount": 100})

    original_require = db._require

    def _deny_join(action: str, collection: str | None = None) -> None:
        if action == "find" and collection == "users":
            raise PermissionDeniedError("denied for join test")
        original_require(action=action, collection=collection)

    db._require = _deny_join  # type: ignore[method-assign]

    with pytest.raises(PermissionDeniedError):
        db.orders.find({}).join("users", on="user_id", foreign_key="_id").execute()


def test_join_invalid_type_raises(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-join-type", path=str(tmp_path))
    db.users.insert({"name": "Alice"})
    db.orders.insert({"user_id": "x", "amount": 10})

    with pytest.raises(ValueError):
        db.orders.find({}).join("users", on="user_id", foreign_key="_id", join_type="cross").execute()
