"""ORM model usage example."""

# ORM module is available in releases with model layer support.
from chronovault.orm import Model, StringField, IntField


class User(Model):
    __collection__ = "users"
    name = StringField(required=True)
    age = IntField(minimum=0)


# Example usage:
# u = User(name="Alice", age=30)
# u.save(db)
# User.find(db, {"age": {"$gte": 18}}).execute()
