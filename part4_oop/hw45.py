from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from part4_oop.interfaces import Cache, HasCache, Policy, Storage

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class DictStorage(Storage[K, V]):
    _data: dict[K, V] = field(default_factory=dict, init=False)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value

    def get(self, key: K) -> V | None:
        return self._data.get(key)

    def exists(self, key: K) -> bool:
        return key in self._data

    def remove(self, key: K) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()


@dataclass
class FIFOPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key not in self._order:
            self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) >= self.capacity:
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        self._order.remove(key) if key in self._order else None

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) > 0


@dataclass
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) >= self.capacity:
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        self._order.remove(key) if key in self._order else None

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) > 0


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)
    _key_order: dict[K, int] = field(default_factory=dict, init=False)
    _order_counter: int = field(default=0, init=False)

    def register_access(self, key: K) -> None:
        if key not in self._key_counter:
            self._key_order[key] = self._order_counter
            self._order_counter += 1
        self._key_counter[key] = self._key_counter.get(key, 0) + 1

    def get_key_to_evict(self) -> K | None:
        if len(self._key_counter) < self.capacity:
            return None

        if not self._key_counter:
            return None

        maybe_removed = list(self._key_counter)
        if len(self._key_counter) > self.capacity:
            last_added_key = max(self._key_order, key=lambda k: self._key_order.get(k, -1))
            maybe_removed = [key for key in maybe_removed if key != last_added_key]
            if not maybe_removed:
                return None
        return min(
            maybe_removed,
            key=lambda k: (self._key_counter[k], self._key_order[k]),
        )

    def remove_key(self, key: K) -> None:
        self._key_counter.pop(key, None)
        self._key_order.pop(key, None)

    def clear(self) -> None:
        self._key_counter.clear()
        self._key_order.clear()
        self._order_counter = 0

    @property
    def has_keys(self) -> bool:
        return len(self._key_counter) > 0


@dataclass
class MIPTCache(Cache[K, V]):
    storage: Storage[K, V]
    policy: Policy[K]

    def set(self, key: K, value: V) -> None:
        if not self.storage.exists(key) and self.policy.has_keys:
            evict_key = self.policy.get_key_to_evict()
            if evict_key is not None:
                self.storage.remove(evict_key)
                self.policy.remove_key(evict_key)

        self.policy.register_access(key)
        self.storage.set(key, value)

    def get(self, key: K) -> V | None:
        if self.storage.exists(key):
            self.policy.register_access(key)
            return self.storage.get(key)
        return None

    def exists(self, key: K) -> bool:
        return self.storage.exists(key)

    def remove(self, key: K) -> None:
        self.storage.remove(key)
        self.policy.remove_key(key)

    def clear(self) -> None:
        self.storage.clear()
        self.policy.clear()


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self.func = func
        self._name = func.__name__

    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> V:
        if instance is None:
            return self  # type: ignore[return-value]

        cache = instance.cache.get(self._name)

        if cache is None:
            cache = self.func(instance)
            instance.cache.set(self._name, cache)

        return cache
