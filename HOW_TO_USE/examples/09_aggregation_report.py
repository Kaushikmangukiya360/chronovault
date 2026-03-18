"""Aggregation report generation."""

import chronovault as cv

db = cv.connect(token="token-agg", org_id="agg-org", path="~/.chronovault")

db.sales.insert_many([
    {"region": "IN", "amount": 1000, "month": "2026-01"},
    {"region": "IN", "amount": 1200, "month": "2026-02"},
    {"region": "US", "amount": 900, "month": "2026-01"},
])

report = db.sales.aggregate([
    {"$group": {"_id": "$region", "total": {"$sum": "$amount"}, "avg": {"$avg": "$amount"}}},
    {"$sort": {"total": -1}},
])
print(report)
