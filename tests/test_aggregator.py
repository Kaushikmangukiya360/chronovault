import chronovault as cv


def test_aggregation_pipeline_group_sort_limit(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-agg", path=str(tmp_path))
    db.orders.insert_many(
        [
            {"country": "IN", "amount": 100, "status": "paid", "items": [1, 2]},
            {"country": "IN", "amount": 300, "status": "paid", "items": [3]},
            {"country": "US", "amount": 200, "status": "paid", "items": [4, 5, 6]},
        ]
    )

    result = db.orders.aggregate(
        [
            {"$match": {"status": "paid"}},
            {
                "$group": {
                    "_id": "$country",
                    "total": {"$sum": "$amount"},
                    "avg": {"$avg": "$amount"},
                    "count": {"$sum": 1},
                    "max": {"$max": "$amount"},
                    "min": {"$min": "$amount"},
                }
            },
            {"$sort": {"total": -1}},
            {"$limit": 1},
        ]
    )

    assert result[0]["_id"] == "IN"
    assert result[0]["total"] == 400
