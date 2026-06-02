from enum import Enum


class RepeatMode(Enum):
    OFF    = ("off",    None,  "Off")
    ALL    = ("all",    "🔁",  "All")
    SINGLE = ("single", "🔂", "Single")

    def __init__(self, key: str, emoji: str | None, label: str):
        self.key   = key
        self.emoji = emoji
        self.label = label

    def next(self) -> "RepeatMode":
        cycle = [RepeatMode.OFF, RepeatMode.ALL, RepeatMode.SINGLE]
        return cycle[(cycle.index(self) + 1) % len(cycle)]

    def __str__(self) -> str:
        return self.key
