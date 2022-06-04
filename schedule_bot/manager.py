from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from schedule_bot import db


class Manager:
    def __init__(self, db: str):
        self.engine = create_engine(db)
        self.session: Session = sessionmaker(self.engine)()

    def get_groups(self):
        return self.session.query(db.Group).all()

    def get_lessons(self) -> List[db.Lesson]:
        return self.session.query(db.Lesson).all()

    def get_authors(self) -> List[db.Lesson]:
        return self.session.query(db.Author).all()

    def get_schedule(self, group, weekday, on_line):
        if type(group) == str:
            group = (
                self.session.query(db.Group)
                .filter(db.Group.group == group)
                .first()
            )
        data = (
            self.session.query(db.Schedule, db.Lesson, db.Author, db.LessonType)
            .filter(
                (db.Schedule.group == group)
                & (db.Schedule.weekday == weekday)
                & (db.Schedule.on_line == on_line)
            )
            .join(db.Lesson, db.Lesson.id == db.Schedule.lesson_id)
            .outerjoin(db.Author, db.Author.id == db.Schedule.author_id)
            .outerjoin(
                db.LessonType, db.LessonType.id == db.Schedule.lesson_type_id
            )
            .order_by(db.Schedule.num)
            .all()
        )
        return data

    def get_lesson_by_num(self, group, weekday, on_line, num, next=False):
        if type(group) == str:
            group = (
                self.session.query(db.Group)
                .filter(db.Group.group == group)
                .first()
            )
        lesson = (
            self.session.query(db.Schedule)
            .filter(
                (db.Schedule.group == group)
                & (db.Schedule.weekday == weekday)
                & (db.Schedule.on_line == on_line)
                & (db.Schedule.num == num)
            )
            .first()
        )
        if next:
            next_lesson = (
                self.session.query(db.Schedule)
                .filter(
                    (db.Schedule.group == group)
                    & (db.Schedule.weekday == weekday)
                    & (db.Schedule.on_line == on_line)
                    & (db.Schedule.num > num)
                )
                .first()
            )
            return lesson, next_lesson
        return lesson

    def get_author_schedule(
        self, author, weekday: int, is_overline: bool
    ) -> List[db.Schedule]:
        if type(author) == str:
            author = (
                self.session.query(db.Author)
                .filter(db.Author.name == author)
                .first()
            )
        data = (
            self.session.query(db.Schedule)
            .filter(
                (db.Schedule.author == author)
                & (db.Schedule.weekday == weekday)
                & (db.Schedule.on_line == is_overline)
            )
            .order_by(db.Schedule.num)
            .all()
        )
        return data

    def get_data(self) -> dict:
        data = {}
        data["lessons"] = self.session.query(db.Lesson).all()
        data["authors"] = self.session.query(db.Author).all()
        data["types"] = self.session.query(db.LessonType).all()
        data["groups"] = self.session.query(db.Group).all()
        return data

    def get_all_users(self) -> List[db.ActiveUser]:
        return self.session.query(db.ActiveUser).all()

    def get_users_in_groups(self, groups: List[str]) -> List[db.ActiveUser]:
        return (
            self.session.query(db.ActiveUser)
            .join(db.Group)
            .filter(db.Group.group.in_(groups))
            .all()
        )

    def add_group(self, group, commit=True) -> int:
        group = db.Group(group)
        self.session.add(group)
        if commit:
            self.session.commit()
        return group.id

    def group_exists(self, name) -> bool:
        return (
            self.session.query(db.Group.group)
            .filter(db.Group.group == name)
            .first()
            is not None
        )

    def group_id(self, group) -> int:
        return (
            self.session.query(db.Group.id)
            .filter(db.Group.group == group)
            .first()
        )

    def add_lesson(self, name, commit=True) -> int:
        lesson = db.Lesson(name)
        self.session.add(lesson)
        if commit:
            self.session.commit()
        return lesson.id

    def add_lessons(self, names: list, commit: bool = True) -> List[int]:
        lessons = [db.Lesson(name) for name in names]
        self.session.add(lessons)
        if commit:
            self.session.commit()
        return [lesson.id for lesson in lessons]

    def add_author(self, name: str, commit=True) -> int:
        author = db.Author(name)
        self.session.add(author)
        if commit:
            self.session.commit()
        return author.id

    def add_authors(self, names: List[str], commit=True) -> List[int]:
        authors = [db.Author(name) for name in names]
        self.session.add_all(authors)
        if commit:
            self.session.commit()
        return [author.id for author in authors]

    def add_schedule(
        self,
        group,
        lesson,
        author,
        lesson_type,
        num,
        weekday,
        is_overline,
        classroom,
        corps=None,
        commit=True,
    ) -> int:
        schedule = db.Schedule(
            group,
            lesson,
            author,
            lesson_type,
            num,
            weekday,
            is_overline,
            classroom,
            corps,
        )
        self.session.add(schedule)
        if commit:
            self.session.commit()
        return schedule.id

    def add_or_upd_schedule(
        self,
        group,
        lesson,
        author,
        lesson_type,
        num,
        weekday,
        is_overline,
        classroom,
        corps=None,
        commit=True,
    ) -> int:
        schedule = (
            self.session.query(db.Schedule).filter(
                (db.Schedule.group_id == group)
                & (db.Schedule.weekday == weekday)
                & (db.Schedule.on_line == is_overline)
                & (db.Schedule.num == num)
            )
        ).first()
        if schedule is None:
            schedule = db.Schedule(
                group,
                lesson,
                author,
                lesson_type,
                num,
                weekday,
                is_overline,
                classroom,
                corps,
            )
            self.session.add(schedule)
        else:
            schedule.lesson_id = lesson
            schedule.author_id = author
            schedule.lesson_type_id = lesson_type
            schedule.classroom = classroom
            schedule.corps = corps

        if commit:
            self.session.commit()
        return schedule.id

    def delete_schedule(
        self, group, weekday, is_overline, num, commit=True
    ) -> None:
        self.session.query(db.Schedule).filter(
            (db.Schedule.group_id == group)
            & (db.Schedule.weekday == weekday)
            & (db.Schedule.on_line == is_overline)
            & (db.Schedule.num == num)
        ).delete(synchronize_session=False)
        if commit:
            self.session.commit()

    def get_user(self, tid):
        return (
            self.session.query(db.ActiveUser, db.Group)
            .filter(db.ActiveUser.tid == tid)
            .outerjoin(db.Group, db.Group.id == db.ActiveUser.group_id)
            .first()
        )

    def get_user_state(self, uid: int) -> int:
        return (
            self.session.query(db.ActiveUser.state)
            .filter(db.ActiveUser.tid == uid)
            .first()[0]
        )

    def set_state(self, uid: int, state: int, commit: bool = True) -> None:
        self.session.query(db.ActiveUser).filter(
            db.ActiveUser.tid == uid
        ).update({"state": state})
        if commit:
            self.session.commit()

    def login_user(
        self, uid: int, group, state: int = 1, commit: bool = True
    ) -> None:
        group = (
            self.session.query(db.Group).filter(db.Group.group == group).first()
        )
        self.session.query(db.ActiveUser).filter(
            db.ActiveUser.tid == uid
        ).update({"group_id": group.id, "state": state})
        if commit:
            self.session.commit()

    def logout_user(self, uid: int, commit: bool = True) -> None:
        self.session.query(db.ActiveUser).filter(
            db.ActiveUser.tid == uid
        ).update({"group_id": None, "state": 0})
        if commit:
            self.session.commit()

    def add_user(self, uid: int, commit=True) -> None:
        user = db.ActiveUser(uid)
        self.session.add(user)
        if commit:
            self.session.commit()

    def user_exists(self, uid: int) -> bool:
        return (
            self.session.query(db.ActiveUser)
            .filter(db.ActiveUser.tid == uid)
            .first()
            is not None
        )


if __name__ == "__main__":

    manager = Manager("sqlite:///lessons.db")

    data = (
        manager.session.query(
            db.Group, db.Schedule, db.Lesson, db.Author, db.LessonType
        )
        .join(db.Schedule, db.Schedule.group_id == db.Group.id)
        .join(db.Lesson, db.Lesson.id == db.Schedule.lesson_id)
        .outerjoin(db.Author, db.Author.id == db.Schedule.author_id)
        .outerjoin(
            db.LessonType, db.LessonType.id == db.Schedule.lesson_type_id
        )
        .order_by(db.Schedule.weekday, db.Schedule.num)
        .all()
    )
    print(*data, sep="\n")
    sch = {}
    for group, schedule, lesson, author, lesson_type in data:
        a = sch.get(group.group, None)
        if a is None:
            sch[group.group] = []
        tp = lesson_type.type if lesson_type is not None else ''
        athr = author.name if author is not None else ''
        sch[group.group].append(
            f"{schedule.num} - {lesson.name} ({tp}) {athr} - {schedule.classroom}"
        )

    for group, lessons in sch.items():
        print(group)
        for lesson in lessons:
            print("  ", lesson)
