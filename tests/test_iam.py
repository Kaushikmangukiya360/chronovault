import pytest

from chronovault.exceptions import PermissionDeniedError
from chronovault.tenant.iam import IAM


def test_viewer_cannot_write() -> None:
    with pytest.raises(PermissionDeniedError):
        IAM.assert_allowed("viewer", "write")


def test_admin_can_do_all_sensitive_actions() -> None:
    IAM.assert_allowed("admin", "write")
    IAM.assert_allowed("admin", "token.issue")
    IAM.assert_allowed("admin", "rotate")
