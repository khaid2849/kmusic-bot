from __future__ import annotations
from trackqueue.abstract_queue import AbstractQueue, Queueable
from typing import TypeVar

T = TypeVar("T", bound=Queueable)


class FairQueue(AbstractQueue[T]):
    def __init__(self, previous: AbstractQueue[T] | None = None):
        super().__init__(previous)

    def add(self, item: T) -> int:
        # Walk backwards to find the last occurrence of this user
        last_index = -1
        for i in range(len(self._list) - 1, -1, -1):
            if self._list[i].get_identifier() == item.get_identifier():
                last_index = i
                break
        last_index += 1

        # From last_index, scan forward collecting unique users until one repeats
        seen: set[int] = set()
        insert_at = last_index
        for insert_at in range(last_index, len(self._list)):
            uid = self._list[insert_at].get_identifier()
            if uid in seen:
                break
            seen.add(uid)
        else:
            insert_at = len(self._list)

        self._list.insert(insert_at, item)
        return insert_at
