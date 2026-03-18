"""User and session storage example."""

import hashlib

import chronovault as cv

db = cv.connect(token="token-auth", org_id="auth-org", path="~/.chronovault")

pw_hash = hashlib.sha256("secret-password".encode()).hexdigest()
uid = db.users.insert({"email": "alice@example.com", "password_hash": pw_hash, "role": "admin"})

session = db.sessions.insert({"user_id": uid, "status": "active"})
print("session:", session)

api_tok = db.issue_token(name="api-gateway", role="viewer", collections=["users"], ip_allowlist=["192.168.0.0/16"], ttl=7200)
print("api token:", api_tok)
