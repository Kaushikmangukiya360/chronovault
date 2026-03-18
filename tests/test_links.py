import time

import pytest

import chronovault as cv
from chronovault.access.linker import Linker
from chronovault.exceptions import TokenExpiredError


def test_generate_and_validate_link(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-links", path=str(tmp_path))
    db.invoices.insert({"n": 1})

    linker = Linker(
        store=db._store,
        tokens_path=db._tenant_root / "tokens.json",
        org_id=db.org_id,
        tenant_token=db.token,
    )

    link = linker.generate_link(
        collection="invoices",
        ttl=60,
        ip="127.0.0.1",
        permissions=["read"],
        single_use=True,
    )
    token = link.split("t=", 1)[1]
    payload = linker.validate_token(token=token, source_ip="127.0.0.1")
    assert payload["collection"] == "invoices"

    with pytest.raises(TokenExpiredError):
        linker.validate_token(token=token, source_ip="127.0.0.1")


def test_link_expiry(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-links-exp", path=str(tmp_path))
    linker = Linker(
        store=db._store,
        tokens_path=db._tenant_root / "tokens.json",
        org_id=db.org_id,
        tenant_token=db.token,
    )

    link = linker.generate_link(
        collection="users",
        ttl=1,
        ip="*",
        permissions=["read"],
        single_use=False,
    )
    token = link.split("t=", 1)[1]
    time.sleep(1.1)
    with pytest.raises(TokenExpiredError):
        linker.validate_token(token=token, source_ip="127.0.0.1")
