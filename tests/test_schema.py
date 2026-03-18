import pytest

import chronovault as cv
from chronovault.exceptions import SchemaValidationError


def test_schema_validation_on_insert_and_update(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-schema", path=str(tmp_path))
    db.users.set_schema(
        {
            "type": "object",
            "required": ["name", "email"],
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "email": {"type": "string", "format": "email"},
                "age": {"type": "integer", "minimum": 0},
            },
            "additionalProperties": False,
        }
    )

    rid = db.users.insert({"name": "Alice", "email": "alice@example.com", "age": 30})
    assert rid

    with pytest.raises(SchemaValidationError):
        db.users.insert({"name": "Bob", "email": "not-an-email", "age": 20})

    with pytest.raises(SchemaValidationError):
        db.users.update({"name": "Alice"}, {"extra": "x"})

    assert db.users.get_schema() is not None
    db.users.drop_schema()
    assert db.users.get_schema() is None
