import chronovault as cv


def test_crud_operations(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-crud", path=str(tmp_path))

    rid = db.users.insert({"name": "Alice", "age": 30})
    assert rid

    ids = db.users.insert_many([{"name": "Bob", "age": 20}, {"name": "Carol", "age": 40}])
    assert len(ids) == 2

    assert len(db.users.find({"name": "Alice"})) == 1
    assert db.users.find_one({"name": "Alice"}) is not None
    assert len(db.users.find({"age": {"$gt": 25}})) == 2
    assert len(db.users.find({"name": {"$in": ["Alice", "Bob"]}})) == 2

    updated = db.users.update({"name": "Alice"}, {"age": 31})
    assert updated == 1
    updated_rich = db.users.update({"age": {"$gte": 30}}, {"active": True})
    assert updated_rich == 2

    alice = db.users.find_one({"name": "Alice"})
    assert alice is not None
    assert alice["_v"] >= 2

    deleted = db.users.delete({"name": "Bob"})
    assert deleted == 1

    bulk = db.users.bulk_write(
        [
            {"insert": {"name": "Dave", "age": 22}},
            {"update": {"filter": {"age": {"$gte": 31}}, "set": {"vip": True}}},
            {"delete": {"filter": {"name": "Carol"}}},
        ]
    )
    assert bulk["inserted"] == 1
    assert bulk["updated"] >= 1
    assert bulk["deleted"] == 1

    assert db.users.count() == 2
