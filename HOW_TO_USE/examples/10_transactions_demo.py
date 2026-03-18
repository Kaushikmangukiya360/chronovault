"""Transaction flow demonstration."""

import chronovault as cv

db = cv.connect(token="token-tx", org_id="tx-org", path="~/.chronovault")

# Transaction manager API is release/profile dependent.
# This fallback demonstrates intent with explicit operations.
a = db.accounts.insert({"name": "A", "balance": 500})
b = db.accounts.insert({"name": "B", "balance": 500})

try:
    db.accounts.update({"_id": a}, {"balance": 400})
    db.accounts.update({"_id": b}, {"balance": 600})
except Exception as exc:
    print("rollback path should trigger in tx mode:", exc)

print(db.accounts.find({}).execute())
