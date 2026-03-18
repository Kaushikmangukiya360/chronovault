import pytest

from chronovault.core.cipher import decrypt_json_payload, encrypt_json_payload
from chronovault.exceptions import TamperDetectedError


def test_tenant_isolation_via_org_scoped_derivation() -> None:
    envelope = encrypt_json_payload('{"x":1}', "same-token", "org-A", 1710000000, "data")

    with pytest.raises(TamperDetectedError):
        decrypt_json_payload(envelope, "same-token", "org-B")
