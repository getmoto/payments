from time import sleep
from backend.expiring_dict import ExpiringDict


def test_expiring_dict():
    storage = ExpiringDict(max_len=100, max_age_seconds=1)

    # Empty initially
    assert storage == {}

    # Storage as normal
    storage["a"] = "b"
    storage["b"] = "c"
    assert storage.items() == [('a', 'b'), ('b', 'c')]
    assert "a" in storage
    assert "b" in storage

    # Wait so the cache is cleared automatically
    sleep(1.1)
    assert storage.items() == []
    assert "a" not in storage
    assert "b" not in storage
