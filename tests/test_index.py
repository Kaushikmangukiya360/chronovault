import pytest

import chronovault as cv
from chronovault.exceptions import IndexNotFoundError, UniqueConstraintError


def test_index_create_list_drop_and_unique(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-index", path=str(tmp_path))
    db.users.insert({"email": "a@example.com", "age": 30})

    name = db.users.create_index("email", unique=True)
    assert name == "email"
    indexes = db.users.list_indexes()
    assert "email" in indexes

    with pytest.raises(UniqueConstraintError):
        db.users.insert({"email": "a@example.com", "age": 31})

    db.users.drop_index("email")
    with pytest.raises(IndexNotFoundError):
        db.users.drop_index("email")
