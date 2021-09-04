import datetime

class Times:
    lesson_begins = [
        datetime.time(8, 30, 0),
        datetime.time(10, 10, 0),
        datetime.time(12, 20, 0),
        datetime.time(14, 0, 0),
        datetime.time(15, 40, 0),
        datetime.time(17, 20, 0),
        datetime.time(19, 0, 0)
    ]

    lesson_ends = [
        datetime.time(10, 0, 0),
        datetime.time(11, 40, 0),
        datetime.time(13, 50, 0),
        datetime.time(15, 30, 0),
        datetime.time(17, 10, 0),
        datetime.time(18, 50, 0),
        datetime.time(20, 30, 0)
    ]

    @staticmethod
    def lesson_time(lesson_num: int, format: str = "%H:%M") -> tuple:
        return (
            Times.lesson_begins[lesson_num + 1].strftime(format),
            Times.lesson_ends[lesson_num + 1].strftime(format),
            )