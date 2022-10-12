from typing import Tuple
from datetime import time

import pytest

from schedule_bot.schedule import num_declination, time_delta


@pytest.fixture
def hour_formats():
    return ('час', 'часа', 'часов')


@pytest.mark.parametrize(
    ('num', 'answer'),
    [
        (10, 'часов'),
        (0, 'часов'),
        (3, 'часа'),
        (1, 'час'),
        (21, 'час'),
    ],
)
def test_num_declination(num: int, answer: str, hour_formats: Tuple[str, ...]):
    assert num_declination(num, hour_formats) == answer


@pytest.mark.parametrize(
    ('start', 'end', 'delta'),
    [
        (time(hour=10), time(hour=12), time(hour=2)),
        (time(hour=1, minute=20), time(hour=2, minute=10), time(minute=50)),
        (time(hour=20), time(hour=4), time(hour=8)),
        (
            time(hour=17, minute=20),
            time(hour=8, minute=30),
            time(hour=15, minute=10),
        ),
    ],
)
def test_time_delta(start: time, end: time, delta: time):
    assert time_delta(start, end) == delta
