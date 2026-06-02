from __future__ import annotations
from queue.abstract_queue import AbstractQueue, Queueable
from typing import TypeVar

T = TypeVar("T", bound=Queueable)


class LinearQueue(AbstractQueue[T]):
    def __init__(self, previous: AbstractQueue[T] | None = None):
        super().__init__(previous)

    def add(self, item: T) -> int:
        self._list.append(item)
        return len(self._list) - 1
