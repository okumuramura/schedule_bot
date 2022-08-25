from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy.orm import Session

from schedule_bot import db
from schedule_bot.manager import orm_function


@orm_function
def get_groups(session: Session = None) -> List[db.Group]:
    return session.query(db.Group).all()


@orm_function
def get_lessons(session: Session = None) -> List[db.Lesson]:
    return session.query(db.Lesson).all()


@orm_function
def get_authors(session: Session = None) -> List[db.Author]:
    return session.query(db.Author).all()


@orm_function
def get_schedule(
    group: Union[str, db.Group],
    weekday: int,
    overline: bool,
    session: Session = None,
):
    if isinstance(group, str):
        group = session.query(db.Group).filter(db.Group.group == group).first()

    data = (
        session.query(db.Schedule, db.Lesson, db.Author, db.LessonType)
        .filter(
            (db.Schedule.group == group)
            & (db.Schedule.weekday == weekday)
            & (db.Schedule.overline == overline)
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


@orm_function
def get_lesson_by_num(
    group: Union[str, db.Group],
    weekday: int,
    overline: bool,
    num: int,
    session: Session = None,
) -> Optional[db.Schedule]:
    if isinstance(group, str):
        group = session.query(db.Group).filter(db.Group.group == group).first()
    lesson = (
        session.query(db.Schedule)
        .filter(
            (db.Schedule.group == group)
            & (db.Schedule.weekday == weekday)
            & (db.Schedule.overline == overline)
            & (db.Schedule.num == num)
        )
        .first()
    )
    return lesson


@orm_function
def get_lesson_with_next(
    group: Union[str, db.Group],
    weekday: int,
    overline: bool,
    num: int,
    session: Session = None,
) -> Tuple[Optional[db.Schedule], Optional[db.Schedule]]:
    lesson = get_lesson_by_num(group, weekday, overline, num, session=session)
    next_lesson = (
        session.query(db.Schedule)
        .filter(
            (db.Schedule.group == group)
            & (db.Schedule.weekday == weekday)
            & (db.Schedule.overline == overline)
            & (db.Schedule.num > num)
        )
        .first()
    )
    return lesson, next_lesson


@orm_function
def get_author_schedule(
    author: Union[str, db.Author],
    weekday: int,
    is_overline: bool,
    session: Session = None,
) -> List[db.Schedule]:
    if isinstance(author, str):
        author = (
            session.query(db.Author).filter(db.Author.name == author).first()
        )
    data = (
        session.query(db.Schedule)
        .filter(
            (db.Schedule.author == author)
            & (db.Schedule.weekday == weekday)
            & (db.Schedule.overline == is_overline)
        )
        .order_by(db.Schedule.num)
        .all()
    )
    return data


@orm_function
def get_data(session: Session = None) -> Dict[str, List[Any]]:
    data = {}
    data["lessons"] = session.query(db.Lesson).all()
    data["authors"] = session.query(db.Author).all()
    data["types"] = session.query(db.LessonType).all()
    data["groups"] = session.query(db.Group).all()
    return data


@orm_function
def get_all_users(session: Session = None) -> List[db.ActiveUser]:
    return session.query(db.ActiveUser).all()


@orm_function
def get_users_in_groups(
    groups: List[str], session: Session = None
) -> List[db.ActiveUser]:
    return (
        session.query(db.ActiveUser)
        .join(db.Group)
        .filter(db.Group.group.in_(groups))
        .all()
    )


@orm_function
def add_group(group: str, commit: bool = True, session: Session = None) -> int:
    group = db.Group(group)
    session.add(group)
    if commit:
        session.commit()
    return group.id


@orm_function
def group_exists(name: str, session: Session = None) -> bool:
    return (
        session.query(db.Group.group).filter(db.Group.group == name).first()
        is not None
    )


@orm_function
def group_id(group: str, session: Session = None) -> int:
    return session.query(db.Group.id).filter(db.Group.group == group).first()


@orm_function
def add_lesson(name: str, commit: bool = True, session: Session = None) -> int:
    lesson = db.Lesson(name)
    session.add(lesson)
    if commit:
        session.commit()
    return lesson.id


@orm_function
def add_lessons(
    names: List[str], commit: bool = True, session: Session = None
) -> List[int]:
    lessons = [db.Lesson(name) for name in names]
    session.add(lessons)
    if commit:
        session.commit()
    return [lesson.id for lesson in lessons]


@orm_function
def add_author(name: str, commit: bool = True, session: Session = None) -> int:
    author = db.Author(name)
    session.add(author)
    if commit:
        session.commit()
    return author.id


@orm_function
def add_authors(
    names: List[str], commit: bool = True, session: Session = None
) -> List[int]:
    authors = [db.Author(name) for name in names]
    session.add_all(authors)
    if commit:
        session.commit()
    return [author.id for author in authors]


@orm_function
def add_schedule(
    group: Union[int, db.Group],
    lesson: Union[int, db.Lesson],
    author: Union[int, db.Author],
    lesson_type: Union[int, db.LessonType],
    num: int,
    weekday: int,
    is_overline: bool,
    classroom: str,
    corps: Optional[str] = None,
    commit: bool = True,
    session: Session = None,
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
    session.add(schedule)
    if commit:
        session.commit()
    return schedule.id


@orm_function
def add_or_upd_schedule(
    group: Union[str, db.Group],
    lesson: Union[str, db.Lesson],
    author: Union[str, db.Author],
    lesson_type: Union[str, db.LessonType],
    num: int,
    weekday: int,
    is_overline: bool,
    classroom: str,
    corps: Optional[str] = None,
    commit: bool = True,
    session: Session = None,
) -> int:
    schedule = (
        session.query(db.Schedule).filter(
            (db.Schedule.group_id == group)
            & (db.Schedule.weekday == weekday)
            & (db.Schedule.overline == is_overline)
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
        session.add(schedule)
    else:
        schedule.lesson_id = lesson
        schedule.author_id = author
        schedule.lesson_type_id = lesson_type
        schedule.classroom = classroom
        schedule.corps = corps

    if commit:
        session.commit()
    return schedule.id


@orm_function
def delete_schedule(
    group: int,
    weekday: int,
    is_overline: bool,
    num: int,
    commit: bool = True,
    session: Session = None,
) -> None:
    session.query(db.Schedule).filter(
        (db.Schedule.group_id == group)
        & (db.Schedule.weekday == weekday)
        & (db.Schedule.overline == is_overline)
        & (db.Schedule.num == num)
    ).delete(synchronize_session=False)
    if commit:
        session.commit()


@orm_function
def get_user(tid: int, session: Session = None):
    return (
        session.query(db.ActiveUser, db.Group)
        .filter(db.ActiveUser.tid == tid)
        .outerjoin(db.Group, db.Group.id == db.ActiveUser.group_id)
        .first()
    )


@orm_function
def set_user_group(
    uid: int, group: str, commit: bool = True, session: Session = None
) -> None:
    group = session.query(db.Group).filter(db.Group.group == group).first()
    session.query(db.ActiveUser).filter(db.ActiveUser.tid == uid).update(
        {'group_id': group.id}
    )
    if commit:
        session.commit()


@orm_function
def drop_user_group(
    uid: int, commit: bool = True, session: Session = None
) -> None:
    session.query(db.ActiveUser).filter(db.ActiveUser.tid == uid).update(
        {"group_id": None}
    )
    if commit:
        session.commit()


@orm_function
def add_user(uid: int, commit: bool = True, session: Session = None) -> None:
    user = db.ActiveUser(uid)
    session.add(user)
    if commit:
        session.commit()


@orm_function
def get_all_vip_users(session: Session = None) -> List[db.ActiveUser]:
    return (
        session.query(db.ActiveUser).filter(db.ActiveUser.vip.is_(True)).all()
    )
