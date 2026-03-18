"""Financial ledger and transfer example."""

import chronovault as cv

db = cv.connect(token="token-fin", org_id="fin-org", path="~/.chronovault")

a = db.accounts.insert({"name": "A", "balance": 1000})
b = db.accounts.insert({"name": "B", "balance": 1000})

# Logical transfer in two updates (transaction API in advanced releases).
db.accounts.update({"_id": a}, {"balance": 900})
db.accounts.update({"_id": b}, {"balance": 1100})
db.ledger.insert({"from": a, "to": b, "amount": 100})

print(db.accounts.find({}).execute())
print(db.ledger.find({}).execute())
print("audit ok:", db.audit_log.verify_integrity())
