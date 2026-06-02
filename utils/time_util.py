from __future__ import annotations
import re
from dataclasses import dataclass


@dataclass
class SeekTime:
    milliseconds: int
    relative: bool


def format_time(duration_ms: int | float) -> str:
    if duration_ms == float("inf") or duration_ms >= 2**62:
        return "LIVE"
    seconds = round(duration_ms / 1000)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def parse_time(args: str) -> SeekTime | None:
    if not args:
        return None
    relative = False
    backwards = False
    if args[0] in ("+", "-"):
        relative = True
        backwards = args[0] == "-"
        args = args[1:]

    ms = _parse_colon_time(args)
    if ms == -1:
        ms = _parse_unit_time(args)
    if ms == -1:
        return None

    if backwards:
        ms = -ms
    return SeekTime(milliseconds=ms, relative=relative)


def parse_colon_time(timestamp: str) -> int:
    return _parse_colon_time(timestamp)


def parse_unit_time(timestr: str) -> int:
    return _parse_unit_time(timestr)


def _parse_colon_time(timestamp: str) -> int:
    parts = re.split(r":+", timestamp)
    if len(parts) > 3:
        return -1
    units: list[float] = [0.0, 0.0, 0.0]
    try:
        for i, part in enumerate(parts):
            if part.startswith(("+", "-")):
                return -1
            units[i + 3 - len(parts)] = float(part.replace(",", "."))
    except ValueError:
        return -1
    return round(units[0] * 3_600_000 + units[1] * 60_000 + units[2] * 1_000)


def _parse_unit_time(timestr: str) -> int:
    timestr = re.sub(r"(?i)(\s|,|and)", "", timestr)
    timestr = re.sub(r"(?i)(-?\d+|[a-z]+)", r"\1 ", timestr).strip()
    vals = timestr.split()
    if not vals:
        return -1
    total = 0
    try:
        for i in range(0, len(vals), 2):
            num = int(vals[i])
            if i + 1 < len(vals):
                unit = vals[i + 1].lower()
                if unit.startswith("m"):
                    num *= 60
                elif unit.startswith("h"):
                    num *= 3_600
                elif unit.startswith("d"):
                    num *= 86_400
            total += num * 1_000
    except (ValueError, IndexError):
        return -1
    return total
