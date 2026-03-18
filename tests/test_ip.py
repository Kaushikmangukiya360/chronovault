import pytest

import chronovault as cv
from chronovault.exceptions import UnauthorizedIPError
from chronovault.tenant.tokens import TokenService


def test_ip_binding_rejects_wrong_ip(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-ip", path=str(tmp_path))
    svc = TokenService(
        store=db._store,
        tokens_path=db._tenant_root / "tokens.json",
        org_id=db.org_id,
        tenant_token=db.token,
    )

    issued = svc.issue_token(
        name="svc-a",
        role="viewer",
        collections=["*"],
        ip_allowlist=["10.0.0.0/8"],
        ttl=None,
    )

    with pytest.raises(UnauthorizedIPError):
        svc.validate(token=issued, source_ip="203.0.113.1")
