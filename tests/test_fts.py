import chronovault as cv


def test_fts_search_and_filter(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-fts", path=str(tmp_path))

    db.products.insert_many(
        [
            {"name": "Wireless Headphones", "description": "Bluetooth noise cancelling", "category": "electronics"},
            {"name": "Wired Mouse", "description": "Gaming mouse usb", "category": "electronics"},
            {"name": "Cooking Pan", "description": "Non stick kitchen cookware", "category": "kitchen"},
        ]
    )

    db.products.enable_fts(fields=["name", "description"])

    rows = db.products.search("wireless bluetooth").execute()
    assert len(rows) >= 1
    assert rows[0]["_score"] > 0

    filtered = db.products.find({"category": "electronics"}).search("mouse gaming").execute()
    assert len(filtered) == 1
    assert filtered[0]["name"] == "Wired Mouse"

    db.products.disable_fts()
    fallback = db.products.search("kitchen").execute()
    assert len(fallback) == 1
    assert fallback[0]["name"] == "Cooking Pan"
