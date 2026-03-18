import chronovault as cv


def test_builder_sort_limit_skip_and_count(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-builder", path=str(tmp_path))
    db.users.insert_many(
        [
            {"name": "Zoe", "age": 30},
            {"name": "Amy", "age": 20},
            {"name": "Ben", "age": 20},
            {"name": "Carl", "age": 40},
        ]
    )

    rows = db.users.find({}).sort([("age", 1), ("name", 1)]).skip(1).limit(2).execute()
    assert [r["name"] for r in rows] == ["Ben", "Zoe"]
    assert db.users.find({"age": 20}).count() == 2
