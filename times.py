import datetime

class Times:
    weekdays = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье"
    ]

    months = [
        {"nominative": "Январь", "genitive": "Января"},
        {"nominative": "Февраль", "genitive": "Февраля"},
        {"nominative": "Март", "genitive": "Марта"},
        {"nominative": "Апрель", "genitive": "Апреля"},
        {"nominative": "Май", "genitive": "Мая"},
        {"nominative": "Июнь", "genitive": "Июня"},
        {"nominative": "Июль", "genitive": "Июля"},
        {"nominative": "Август", "genitive": "Августа"},
        {"nominative": "Сентябрь", "genitive": "Сентября"},
        {"nominative": "Октябрь", "genitive": "Октября"},
        {"nominative": "Ноябрь", "genitive": "Ноября"},
        {"nominative": "Декабрь", "genitive": "Декабря"},
    ]

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
            Times.lesson_begins[lesson_num - 1].strftime(format),
            Times.lesson_ends[lesson_num - 1].strftime(format),
            )

    @staticmethod
    def today_weekday() -> str:
        return Times.weekdays[datetime.datetime.today().weekday()]

    @staticmethod
    def tomorrow_weekday() -> str:
        return Times.weekdays[(datetime.datetime.today().weekday() + 1) % 7]

    @staticmethod
    def today_month(case = "nominative") -> str:
        allowed_cases = ["nominative", "genitive"]
        if case in allowed_cases:
            return Times.months[(datetime.datetime.today().month - 1)]
        else:
            assert KeyError(f"Wrong case!, allowed: {', '.join(allowed_cases)}.")

    @staticmethod
    def today_date() -> str:
        return f"{datetime.datetime.today().day} {Times.today_month('genitive')}"

