import logging

from sqlalchemy.orm import Session

from schedule_bot import db
from schedule_bot.manager import manager, orm_function

__log_format = r'[%(levelname)s] %(message)s'

logger = logging.Logger(__name__, logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(__log_format))
logger.addHandler(handler)


class Updater:
    @orm_function
    def clear_schedule(self, session: Session = None) -> None:
        session.query(db.Schedule).delete()
        session.commit()

    @orm_function
    def add_lessons(self, lessons_set, session: Session = None) -> None:
        new_lessons = []
        for lesson in lessons_set:
            lesson_id = (
                session.query(db.Lesson.id)
                .filter(db.Lesson.name == lesson)
                .first()
            )
            if lesson_id is None:
                new_lessons.append(db.Lesson(lesson))

        session.add_all(new_lessons)
        session.commit()

    @orm_function
    def add_authors(self, authors_set, session: Session = None) -> None:
        new_authors = []
        for author in authors_set:
            author_id = (
                session.query(db.Author.id)
                .filter(db.Author.name == author)
                .first()
            )
            if author_id is None:
                # a_id = manager.add_author(a, commit=False)
                new_authors.append(db.Author(author))

        session.add_all(new_authors)
        session.commit()

    @orm_function
    def add_group(self, group, schedule, session: Session = None) -> None:
        g = session.query(db.Group.id).filter(db.Group.group == group).first()
        if g is None:
            g = manager.add_group(group, session=session)
        else:
            g = g[0]

        weekday: int
        number: int
        is_overline: bool

        for i, lesson in enumerate(schedule):
            if lesson is None:
                continue
            l_id = (
                session.query(db.Lesson.id)
                .filter(db.Lesson.name == lesson.name)
                .first()
            )
            if l_id is None:
                l_id = manager.add_lesson(lesson.name, session=session)
            else:
                l_id = l_id[0]
            weekday = i // 14
            is_overline = i % 2 == 0
            number = i % 14 // 2 + 1

            if lesson.author is not None:
                a_id = (
                    session.query(db.Author.id)
                    .filter(db.Author.name == lesson.author)
                    .first()
                )
                if a_id is None:
                    a_id = manager.add_author(lesson.author, session=session)
                else:
                    a_id = a_id[0]
            else:
                a_id = None

            if lesson.lesson_type is not None:
                t_id = (
                    session.query(db.LessonType.id)
                    .filter(db.LessonType.type == lesson.lesson_type)
                    .first()
                )
                if t_id is None:
                    print('No lesson type in db: ' + lesson.lesson_type)
                else:
                    t_id = t_id[0]
            else:
                t_id = None

            manager.add_schedule(
                g,
                l_id,
                a_id,
                t_id,
                number,
                weekday,
                is_overline,
                lesson.auditory,
                commit=False,
                session=session,
            )

        session.commit()
