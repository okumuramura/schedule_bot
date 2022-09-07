from typing import Tuple

import pytest

from schedule_bot.schedule import num_declination


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
    ]
)
def test_num_declination(num: int, answer: str, hour_formats: Tuple[str, ...]):
    assert num_declination(num, hour_formats) == answer
