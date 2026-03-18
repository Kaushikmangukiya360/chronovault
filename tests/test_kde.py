from chronovault.core.kde import derive_key


def test_derive_key_deterministic_for_same_input() -> None:
    key1 = derive_key("secret", "orgA", 1710000000)
    key2 = derive_key("secret", "orgA", 1710000000)
    assert key1 == key2
    assert len(key1) == 32


def test_derive_key_changes_with_timestamp() -> None:
    key1 = derive_key("secret", "orgA", 1710000000)
    key2 = derive_key("secret", "orgA", 1710000001)
    assert key1 != key2
