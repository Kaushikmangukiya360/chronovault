import time

import pytest

import chronovault as cv
from chronovault.exceptions import TokenExpiredError, TokenRevokedError
from chronovault.tenant.tokens import TokenService


def test_token_ttl_revocation_and_single_use(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-tokens", path=str(tmp_path))
    svc = TokenService(
        store=db._store,
        tokens_path=db._tenant_root / "tokens.json",
        org_id=db.org_id,
        tenant_token=db.token,
    )

    short = svc.issue_token(name="short", role="viewer", ttl=1)
    svc.validate(token=short, source_ip="127.0.0.1")
    time.sleep(1.1)
    with pytest.raises(TokenExpiredError):
        svc.validate(token=short, source_ip="127.0.0.1")

    revoke_me = svc.issue_token(name="revokable", role="viewer", ttl=None)
    svc.revoke_token("revokable")
    with pytest.raises(TokenRevokedError):
        svc.validate(token=revoke_me, source_ip="127.0.0.1")

    one = svc.issue_token(name="one", role="viewer", ttl=None, single_use=True)
    svc.validate(token=one, source_ip="127.0.0.1")
    with pytest.raises(TokenExpiredError):
        svc.validate(token=one, source_ip="127.0.0.1")
