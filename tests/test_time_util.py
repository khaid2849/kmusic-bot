import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from utils.time_util import format_time, parse_time, parse_colon_time, parse_unit_time


# ── format_time ──────────────────────────────────────────────────────────────

def test_format_seconds():
    assert format_time(5_000)  == "0:05"
    assert format_time(9_000)  == "0:09"
    assert format_time(59_000) == "0:59"


def test_format_minutes():
    assert format_time(60_000)  == "1:00"
    assert format_time(330_000) == "5:30"
    assert format_time(599_000) == "9:59"


def test_format_hours():
    assert format_time(3_600_000) == "1:00:00"
    assert format_time(3_661_000) == "1:01:01"
    assert format_time(7_322_000) == "2:02:02"


def test_format_live():
    assert format_time(float("inf")) == "LIVE"
    assert format_time(2**62)        == "LIVE"


def test_format_zero():
    assert format_time(0) == "0:00"


# ── parse_colon_time ─────────────────────────────────────────────────────────

def test_parse_colon_ss():
    assert parse_colon_time("5")    == 5_000
    assert parse_colon_time("30")   == 30_000


def test_parse_colon_mmss():
    assert parse_colon_time("1:30") == 90_000
    assert parse_colon_time("0:05") == 5_000
    assert parse_colon_time("5:00") == 300_000


def test_parse_colon_hhmmss():
    assert parse_colon_time("1:01:01") == 3_661_000
    assert parse_colon_time("0:00:05") == 5_000


def test_parse_colon_invalid():
    assert parse_colon_time("abc")       == -1
    assert parse_colon_time("1:2:3:4")   == -1
    assert parse_colon_time("+1:00")     == -1


# ── parse_unit_time ──────────────────────────────────────────────────────────

def test_parse_unit_seconds():
    assert parse_unit_time("5s")  == 5_000
    assert parse_unit_time("30s") == 30_000


def test_parse_unit_minutes():
    assert parse_unit_time("1m")    == 60_000
    assert parse_unit_time("1m30")  == 90_000
    assert parse_unit_time("1m30s") == 90_000


def test_parse_unit_hours():
    assert parse_unit_time("1h")     == 3_600_000
    assert parse_unit_time("1h30m")  == 5_400_000


def test_parse_unit_invalid():
    assert parse_unit_time("abc") == -1


# ── parse_time ───────────────────────────────────────────────────────────────

def test_parse_time_absolute_colon():
    result = parse_time("1:30")
    assert result is not None
    assert result.milliseconds == 90_000
    assert result.relative     is False


def test_parse_time_absolute_unit():
    result = parse_time("1m30s")
    assert result is not None
    assert result.milliseconds == 90_000
    assert result.relative     is False


def test_parse_time_relative_forward():
    result = parse_time("+0:30")
    assert result is not None
    assert result.milliseconds == 30_000
    assert result.relative     is True


def test_parse_time_relative_backward():
    result = parse_time("-1:00")
    assert result is not None
    assert result.milliseconds == -60_000
    assert result.relative     is True


def test_parse_time_invalid():
    assert parse_time("")    is None
    assert parse_time("abc") is None


def test_parse_time_edge_zero():
    result = parse_time("0:00")
    assert result is not None
    assert result.milliseconds == 0
