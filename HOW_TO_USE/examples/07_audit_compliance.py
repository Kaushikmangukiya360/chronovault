"""Audit and compliance workflow."""

import chronovault as cv

db = cv.connect(token="token-audit", org_id="audit-org", path="~/.chronovault")

db.logs.insert({"event": "login", "actor": "alice"})
db.logs.insert({"event": "export", "actor": "bob"})

print("tail:", db.audit_log.tail(n=10))
print("filter:", db.audit_log.filter(event="collection.write", collection="logs"))
print("integrity:", db.audit_log.verify_integrity())
db.audit_log.export("audit_evidence.json")
db.export_compliance_report("compliance_report.json")
