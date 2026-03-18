# 06 Aggregation

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Aggregation pipelines support operational analytics without moving data outside your encrypted store.

```python
report = db.orders.aggregate([
    {"$match": {"status": "paid"}},
    {"$group": {
        "_id": "$country",
        "total": {"$sum": "$amount"},
        "avg": {"$avg": "$amount"},
        "count": {"$sum": 1},
        "max": {"$max": "$amount"},
        "min": {"$min": "$amount"}
    }},
    {"$sort": {"total": -1}},
    {"$limit": 10}
])
```

Stages: `$match`, `$group`, `$sort`, `$limit`, `$skip`, `$project`, `$unwind`, `$count`, `$addFields`.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
