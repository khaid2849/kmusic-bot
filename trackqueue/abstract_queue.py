from __future__ import annotations
import random
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Queueable(ABC):
    @abstractmethod
    def get_identifier(self) -> int: ...


class AbstractQueue(ABC, Generic[T]):
    def __init__(self, previous: "AbstractQueue[T] | None" = None):
        self._list: list[T] = list(previous._list) if previous is not None else []

    @abstractmethod
    def add(self, item: T) -> int: ...

    def add_at(self, index: int, item: T) -> None:
        if index >= len(self._list):
            self._list.append(item)
        else:
            self._list.insert(index, item)

    def size(self) -> int:
        return len(self._list)

    def pull(self) -> T:
        return self._list.pop(0)

    def is_empty(self) -> bool:
        return len(self._list) == 0

    def get_list(self) -> list[T]:
        return self._list

    def get(self, index: int) -> T:
        return self._list[index]

    def remove(self, index: int) -> T:
        return self._list.pop(index)

    def remove_all(self, identifier: int) -> int:
        before = len(self._list)
        self._list = [item for item in self._list if item.get_identifier() != identifier]
        return before - len(self._list)

    def clear(self) -> None:
        self._list.clear()

    def shuffle(self, identifier: int) -> int:
        indices = [i for i, item in enumerate(self._list) if item.get_identifier() == identifier]
        shuffled = indices[:]
        random.shuffle(shuffled)
        for orig, new in zip(indices, shuffled):
            self._list[orig], self._list[new] = self._list[new], self._list[orig]
        return len(indices)

    def skip(self, number: int) -> None:
        if number > 0:
            del self._list[:number]

    def move_item(self, from_index: int, to_index: int) -> T:
        item = self._list.pop(from_index)
        self._list.insert(to_index, item)
        return item
