from __future__ import annotations
from enum import Enum


class QueueType(Enum):
    FAIR   = ("fair",   "🔢", "Fair")
    LINEAR = ("linear", "⏩", "Linear")

    def __init__(self, key: str, emoji: str, label: str):
        self.key   = key
        self.emoji = emoji
        self.label = label

    def create_instance(self, previous=None):
        from queue.fair_queue import FairQueue
        from queue.linear_queue import LinearQueue
        if self == QueueType.FAIR:
            return FairQueue(previous)
        return LinearQueue(previous)

    @classmethod
    def from_str(cls, value: str) -> "QueueType":
        for member in cls:
            if member.key == value.lower():
                return member
        raise ValueError(f"Unknown queue type: {value}")

    @classmethod
    def names(cls) -> list[str]:
        return [m.key for m in cls]

    def __str__(self) -> str:
        return self.key
