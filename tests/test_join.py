import chronovault as cv


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
