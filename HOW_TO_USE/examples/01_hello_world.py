"""Hello world walkthrough for chronovault."""

import json
import os

import chronovault as cv

TOKEN = os.environ.get("CV_TOKEN", "replace-with-secure-token")

# Connect to local encrypted vault storage.
db = cv.connect(token=TOKEN, org_id="hello-org", path="~/.chronovault")

# Create one user record.
uid = db.users.insert({"name": "Alice", "email": "alice@example.com", "age": 30})
print("inserted:", uid)

# Read records with query builder.
print("all:", db.users.find({}).execute())
print("one:", db.users.find_one({"_id": uid}))

# Update and verify.
db.users.update({"_id": uid}, {"age": 31})
print("after update:", db.users.find_one({"_id": uid}))

# Show encrypted file envelope (not plaintext).
p = os.path.expanduser("~/.chronovault/tenants/hello-org/collections/users/data_000.json")
with open(p, "r", encoding="utf-8") as f:
    print("encrypted envelope:")
    print(json.dumps(json.load(f), indent=2))

# Delete and verify.
db.users.delete({"_id": uid})
print("count:", db.users.count())
