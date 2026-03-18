import chronovault as cv


def test_query_operators_nested_and_projection(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-query", path=str(tmp_path))
    db.users.insert_many(
        [
            {"name": "Alice", "age": 30, "tags": ["python", "security"], "address": {"city": "Mumbai"}},
            {"name": "Bob", "age": 17, "tags": ["python"], "address": {"city": "Delhi"}},
            {"name": "Carol", "age": 70, "address": {"city": "Mumbai"}},
        ]
    )

    assert len(db.users.find({"age": {"$gte": 18}}).execute()) == 2
    assert len(db.users.find({"age": {"$lt": 18}}).execute()) == 1
    assert len(db.users.find({"name": {"$regex": "^A"}}).execute()) == 1
    assert len(db.users.find({"address.city": "Mumbai"}).execute()) == 2
    assert len(db.users.find({"tags": {"$all": ["python", "security"]}}).execute()) == 1
    assert len(db.users.find({"tags": {"$size": 1}}).execute()) == 1
    assert len(db.users.find({"phone": {"$exists": False}}).execute()) == 3

    projected = db.users.find({"name": "Alice"}).project({"name": 1, "address.city": 1, "_id": 0}).first()
    assert projected == {"name": "Alice", "address": {"city": "Mumbai"}}
