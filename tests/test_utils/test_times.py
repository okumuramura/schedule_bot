from freezegun import freeze_time
import pytest

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
