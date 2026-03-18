"""Healthcare-oriented role and audit demo."""

import chronovault as cv

db = cv.connect(token="token-health", org_id="health-org", path="~/.chronovault")

db.patients.insert({"name": "John", "dob": "1987-01-02", "mrn": "MRN-1001"})
db.records.insert({"patient": "MRN-1001", "diagnosis": "hypertension"})
db.prescriptions.insert({"patient": "MRN-1001", "medication": "Drug-A"})

nurse_token = db.issue_token(name="nurse", role="viewer", collections=["patients", "records"], ip_allowlist=["10.10.0.0/16"], ttl=3600)
print("nurse token:", nurse_token)

print("audit tail:", db.audit_log.tail(20))
db.audit_log.export("health_audit.json")
