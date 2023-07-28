from time import sleep
from backend.expiring_dict import ExpiringDict


def test_expiring_dict_by_time():
    storage = ExpiringDict(max_len=100, max_age_seconds=1)

    # Empty initially
    assert storage == {}

    # Storage as normal
    storage["a"] = "b"
    storage["b"] = "c"
    assert storage.items() == [('a', 'b'), ('b', 'c')]
    assert storage.values() == ["b", "c"]
    assert "a" in storage
    assert "b" in storage

    # Wait so the cache is cleared automatically
    sleep(1.1)
    assert "a" not in storage
    assert storage.items() == []
    assert storage.values() == []
    assert "b" not in storage


def test_expiring_dict_by_size():
    storage = ExpiringDict(max_len=2, max_age_seconds=1)

    storage["a"] = "k1"
    storage["b"] = "k2"
    assert storage.items() == [('a', 'k1'), ('b', 'k2')]

    # Push new item -> kicks first item
    storage["c"] = "k3"
    assert storage.items() == [('b', 'k2'), ("c", "k3")]

    # Reset existing item -> resets time
    storage["b"] = "k4"
    assert storage.items() == [('c', 'k3'), ("b", "k4")]
