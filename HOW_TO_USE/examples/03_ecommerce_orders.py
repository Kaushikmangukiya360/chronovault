"""Ecommerce workflow demo."""

import chronovault as cv

db = cv.connect(token="token-ecom", org_id="shop", path="~/.chronovault")

u = db.users.insert({"name": "Buyer", "country": "IN"})
p = db.products.insert({"name": "Keyboard", "price": 1200, "stock": 10})

db.orders.insert({"user_id": u, "product_id": p, "amount": 1200, "status": "paid"})
db.invoices.insert({"user_id": u, "total": 1200, "currency": "INR"})

joined = db.orders.find({"status": "paid"}).join("users", on="user_id", foreign_key="_id").join("products", on="product_id", foreign_key="_id").execute()
print("joined:", joined)

report = db.orders.aggregate([
    {"$match": {"status": "paid"}},
    {"$group": {"_id": "$status", "revenue": {"$sum": "$amount"}}},
])
print("report:", report)
