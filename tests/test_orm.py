import chronovault as cv
from chronovault.orm import EmailField, IntField, Model, StringField


class User(Model):
    __collection__ = "users"

    name = StringField(required=True)
    email = EmailField(required=True)
    age = IntField(minimum=0)


def test_orm_model_save_find_update_delete(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-orm", path=str(tmp_path))

    user = User(name="Alice", email="alice@example.com", age=30)
    user.save(db)
    assert user._id is not None

    found = User.find_one(db, {"email": "alice@example.com"})
    assert found is not None
    assert found.name == "Alice"

    found.age = 31
    found.save(db)
    updated = User.find_one(db, {"email": "alice@example.com"})
    assert updated is not None
    assert updated.age == 31

    deleted = updated.delete(db)
    assert deleted == 1
    assert User.find_one(db, {"email": "alice@example.com"}) is None
