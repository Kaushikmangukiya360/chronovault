from concurrent.futures import ThreadPoolExecutor

import chronovault as cv


def test_concurrent_writes_remain_consistent(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-conc", path=str(tmp_path))

    def _insert(i: int) -> None:
        db.logs.insert({"i": i})

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(_insert, range(40)))

    assert db.logs.count() == 40
    assert db.audit_log.verify_integrity() is True
    assert len(db.audit_log.tail(1000)) >= 40
