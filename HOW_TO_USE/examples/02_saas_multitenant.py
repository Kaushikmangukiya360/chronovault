"""Multi-tenant isolation demonstration."""

import chronovault as cv

acme = cv.connect(token="token-acme", org_id="acme-corp", path="~/.chronovault")
beta = cv.connect(token="token-beta", org_id="beta-saas", path="~/.chronovault")
gamma = cv.connect(token="token-gamma", org_id="gamma-health", path="~/.chronovault")

acme.users.insert({"tenant": "acme", "name": "Alice"})
beta.users.insert({"tenant": "beta", "name": "Bob"})
gamma.users.insert({"tenant": "gamma", "name": "Carol"})

print("acme:", acme.users.find({}).execute())
print("beta:", beta.users.find({}).execute())
print("gamma:", gamma.users.find({}).execute())

viewer_token = acme.issue_token(name="svc-reports", role="viewer", collections=["users"], ip_allowlist=["*"], ttl=None)
print("acme viewer token issued:", viewer_token)
