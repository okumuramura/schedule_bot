from typing import Tuple, Union, List, Optional
import datetime

from schedule_bot import db
from schedule_bot.utils.times import Times
from schedule_bot.manager import manager


class NowAndNext:
    def __init__(
        self,
        now_lesson: db.Schedule,
        next_lesson: db.Schedule,
        time_remain: datetime.time,
        time_until: datetime.time,
    ):

        self.now = now_lesson
        self.next = next_lesson
        self.remain = time_remain
        self.until = time_until

    def __str__(self) -> str:
        sep = "\n"
        if self.now is not None:
            _now = f"Сейчас:\n{self.now.just_name()}\nзакончится через {self.time_to_str(self.remain)}\n"
        else:
            _now = "Сейчас у вас нет пары\n"
        if self.next is not None:
            _next = f"Потом:\n{self.next.just_name()}\nначало через {self.time_to_str(self.until)}"
        else:
            _next = "Похоже на сегодня это всё!"
            sep = ""
        return _now + sep + _next

    def time_to_str(self, time: datetime.time) -> str:
        hour_str = ["час", "часа", "часов"]
        minut_str = ["минуту", "минуты", "минут"]
        second_str = ["секунду", "секунды", "секунд"]
        hour = time.hour
        minute = time.minute
        second = time.second
        if hour == 0:
            _hour = ""
        else:
            _hour = f"{hour} {self.num_declination(hour, hour_str)}"
        if minute == 0:
            _minute = ""
        else:
            _minute = f"{minute} {self.num_declination(minute, minut_str)}"
        if second == 0:
            _second = ""
        else:
            _second = f"{second} {self.num_declination(second, second_str)}"
        return " ".join([_hour, _minute, _second])

    def num_declination(self, num: int, words: Tuple[str]) -> str:
        second_from_end = num % 100 // 10
        first_from_end = num % 10
        if (
            second_from_end == 1
            or first_from_end == 0
            or (5 <= first_from_end <= 9)
        ):
            return words[2]
        elif first_from_end == 1:
            return words[0]
        else:
            return words[1]


class Schedule:
    def __init__(self) -> None:
        self._time_schedule = ""
        for i, (b, e) in enumerate(zip(Times.lesson_begins, Times.lesson_ends)):
            self._time_schedule += (
                f"{i+1}. {b.strftime('%H:%M')} - {e.strftime('%H:%M')}\n"
            )

    def date(self, add: int = 0) -> Tuple[int, int]:
        if add == 0:
            week, weekday = datetime.datetime.now().isocalendar()[1:]
        else:
            week, weekday = (
                datetime.datetime.now() + datetime.timedelta(days=add)
            ).isocalendar()[1:]
        return week, weekday

    def now(self, group: Union[str, db.Group]) -> NowAndNext:
        week, weekday = datetime.datetime.now().isocalendar()[1:]
        now_time = datetime.datetime.now().time()
        cur_lesson = -1
        for lesson_num, (begin_time, end_time) in enumerate(
            zip(Times.lesson_begins, Times.lesson_ends)
        ):
            if now_time <= end_time:
                cur_lesson = lesson_num + 1
                break
        now_lesson, next_lesson = manager.get_lesson_with_next(
            group, weekday - 1, self.is_overline(week), cur_lesson
        )
        if (
            not (
                Times.lesson_begins[cur_lesson - 1]
                <= now_time
                <= Times.lesson_ends[cur_lesson - 1]
            )
            and now_lesson is not None
        ):
            now_lesson, next_lesson = None, now_lesson
        if now_lesson is not None:
            time_remain = self.time_delta(
                Times.lesson_ends[cur_lesson - 1], now_time
            )
        else:
            time_remain = None

        if next_lesson is not None:
            time_until = self.time_delta(
                Times.lesson_begins[next_lesson.num - 1], now_time
            )
        else:
            time_until = None

        now_next = NowAndNext(now_lesson, next_lesson, time_remain, time_until)

        return now_next

    def today(self, group: Union[str, db.Group]) -> List[str]:
        week, weekday = datetime.datetime.now().isocalendar()[1:]
        schedule = manager.get_schedule(
            group, weekday - 1, self.is_overline(week)
        )
        str_schedule = []
        for sch in schedule:
            str_schedule.append(str(sch[0]))

        return str_schedule

    def tomorrow(self, group: Union[str, db.Group]) -> List[str]:
        week, weekday = (
            datetime.datetime.now() + datetime.timedelta(days=1)
        ).isocalendar()[1:]
        schedule = manager.get_schedule(
            group, weekday - 1, self.is_overline(week)
        )
        str_schedule = []
        for sch in schedule:
            str_schedule.append(str(sch[0]))

        return str_schedule

    def day_schedule(self, group: Union[str, db.Group], day: int, is_overline: bool) -> List[str]:
        schedule = manager.get_schedule(group, day, is_overline)
        str_schedule = []
        for sch in schedule:
            str_schedule.append(str(sch[0]))

        return str_schedule

    def time_schedule(self) -> str:
        return self._time_schedule

    def is_overline(self, week: Optional[int] = None, add: int = 0) -> bool:
        if week is None:
            return True if self.date(add=add)[0] % 2 != 0 else False
        return not week % 2 == 0

    def time_delta(self, stime: datetime.time, etime: datetime.time) -> datetime.datetime:
        d1 = datetime.timedelta(
            hours=stime.hour, minutes=stime.minute, seconds=stime.second
        )
        d2 = datetime.timedelta(
            hours=etime.hour, minutes=etime.minute, seconds=etime.second
        )
        return (datetime.datetime.min + (d1 - d2)).time()
