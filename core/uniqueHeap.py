from __future__ import annotations

import heapq
from typing import TypeVar, Callable, Generic

T = TypeVar("T")


class UniqueHeap(Generic[T]):
    def __init__(self, elements: list[T] = None, key: Callable[[T], int] = lambda x: x, max_size: int = None):
        self.elements = []
        self._mapping = {}
        self._key = key
        self._max_size = max_size

        if elements is not None:
            for item in elements:
                prio = self._key(item)
                self._mapping[prio] = (prio, item)

            keys = sorted(self._mapping.keys())[-self._max_size:]
            self.elements = [self._mapping[k] for k in keys]
            self._mapping = {e[0]: e for e in self.elements}

            heapq.heapify(self.elements)

    def empty(self) -> bool:
        return not self.elements

    def put(self, item: T):
        prio = self._key(item)
        if prio in self._mapping:
            return

        entry = (prio, item)
        self._mapping[prio] = entry

        if self._max_size is not None and len(self.elements) >= self._max_size:
            popped = heapq.heappushpop(self.elements, entry)
            del self._mapping[popped[0]]
        else:
            heapq.heappush(self.elements, entry)

    def pop(self) -> T:
        popped = heapq.heappop(self.elements)
        del self._mapping[popped[0]]
        return popped[1]

    def merge(self, other: UniqueHeap):
        for prio, item in other.elements:
            if prio not in self._mapping:
                self.put(item)
