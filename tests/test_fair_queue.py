import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from queue.fair_queue import FairQueue
from queue.abstract_queue import Queueable


class Item(Queueable):
    def __init__(self, user_id: int):
        self.user_id = user_id

    def get_identifier(self) -> int:
        return self.user_id


@pytest.fixture
def q():
    return FairQueue(None)


def ids(queue) -> list[int]:
    return [queue.get(i).get_identifier() for i in range(queue.size())]


# ── Basic operations ─────────────────────────────────────────────────────────

def test_empty_on_init(q):
    assert q.is_empty()
    assert q.size() == 0


def test_single_user(q):
    q.add(Item(1)); q.add(Item(1)); q.add(Item(1))
    assert ids(q) == [1, 1, 1]


def test_pull_returns_first(q):
    q.add(Item(1)); q.add(Item(2))
    assert q.pull().get_identifier() == 1
    assert q.size() == 1


def test_add_at_front(q):
    q.add(Item(1)); q.add(Item(2))
    q.add_at(0, Item(99))
    assert q.get(0).get_identifier() == 99


def test_remove_by_index(q):
    q.add(Item(1)); q.add(Item(2)); q.add(Item(3))
    removed = q.remove(1)
    assert removed.get_identifier() == 2
    assert q.size() == 2


def test_remove_all(q):
    q.add(Item(1)); q.add(Item(2)); q.add(Item(1))
    count = q.remove_all(1)
    assert count == 2
    assert q.size() == 1
    assert q.get(0).get_identifier() == 2


def test_clear(q):
    q.add(Item(1)); q.add(Item(2))
    q.clear()
    assert q.is_empty()


def test_move_item(q):
    q.add(Item(1)); q.add(Item(2)); q.add(Item(3))
    q.move_item(2, 0)
    assert ids(q) == [3, 1, 2]


def test_skip(q):
    for i in [1, 2, 3, 4]:
        q.add(Item(i))
    q.skip(2)
    assert ids(q) == [3, 4]


# ── FairQueue interleaving ───────────────────────────────────────────────────

def test_two_users_interleave(q):
    q.add(Item(1)); q.add(Item(2))
    q.add(Item(1)); q.add(Item(2))
    assert ids(q) == [1, 2, 1, 2]


def test_three_users_interleave(q):
    q.add(Item(1)); q.add(Item(2)); q.add(Item(3))
    q.add(Item(1)); q.add(Item(2)); q.add(Item(3))
    assert ids(q) == [1, 2, 3, 1, 2, 3]


def test_late_joiner_inserted_before_second_turn(q):
    # A queues twice, then B queues once -> A, B, A
    q.add(Item(1)); q.add(Item(1))
    q.add(Item(2))
    assert ids(q) == [1, 2, 1]


def test_single_user_multiple_tracks(q):
    for _ in range(5):
        q.add(Item(1))
    assert all(q.get(i).get_identifier() == 1 for i in range(5))


def test_user_joins_mid_queue(q):
    # A,A,A queued, then B queues -> A, B, A, A
    q.add(Item(1)); q.add(Item(1)); q.add(Item(1))
    q.add(Item(2))
    result = ids(q)
    assert result[0] == 1
    assert result[1] == 2


def test_shuffle_only_affects_user(q):
    q.add(Item(1)); q.add(Item(2)); q.add(Item(1))
    count = q.shuffle(1)
    assert count == 2
    # user 2's track must still be present
    assert any(q.get(i).get_identifier() == 2 for i in range(q.size()))
