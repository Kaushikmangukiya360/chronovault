"""Full-text search style example."""

import chronovault as cv

db = cv.connect(token="token-search", org_id="search-org", path="~/.chronovault")

# Search API requires versions with FTS support.
db.products.insert_many([
    {"name": "Wireless Headphones", "description": "Bluetooth noise cancelling", "category": "electronics"},
    {"name": "Wired Earbuds", "description": "3.5mm budget audio", "category": "electronics"},
])

rows = db.products.find({"category": "electronics"}).search("wireless bluetooth").sort("_score", -1).execute()
print(rows)
