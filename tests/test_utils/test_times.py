import pytest
from freezegun import freeze_time

from schedule_bot.utils.times import Times


@freeze_time('2022-09-11')  # sunday
def test_weekday_function():
    assert Times.today_weekday() == Times.weekdays[6]
    assert Times.tomorrow_weekday() == Times.weekdays[0]


def test_today_month_with_wrong_case():
    with pytest.raises(KeyError):
        Times.today_month(case='wrong_case')


@freeze_time('2022-01-01')  # January
def test_today_month():
    assert Times.today_month(case='nominative') == Times.months[0]['nominative']
    assert Times.today_month(case='genitive') == Times.months[0]['genitive']


@freeze_time('2022-01-01')  # 1st January
def test_today_date_function():
    assert Times.today_date() == '1 Января'


def test_lesson_time():
    base_format = '%H:%M'
    lesson_start = Times.lesson_begins[0].strftime(base_format)
    lesson_end = Times.lesson_ends[0].strftime(base_format)

    assert Times.lesson_time(1) == (lesson_start, lesson_end)


def test_lesson_time_with_invalid_lesson_num():
    with pytest.raises(IndexError):
        Times.lesson_time(-1)

    with pytest.raises(IndexError):
        Times.lesson_time(99)
