from __future__ import annotations

from typing import Any, List, Optional, Union

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from schedule_bot import Base, engine, logger
from schedule_bot.utils.times import Times


class Group(Base):
    __tablename__ = 'groups'

    id: int = Column(Integer, primary_key=True)
    group: str = Column(String(20), nullable=False)

    schedules: List[Schedule] = relationship('Schedule', back_populates='group')
    users: List[ActiveUser] = relationship('ActiveUser', back_populates='group')

    def __init__(self, group: str) -> None:
        self.group = group

    def __repr__(self) -> str:
        return f'<Group {self.group}>'

    def __str__(self) -> str:
        return self.group

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.group == other
        return False


class Author(Base):
    __tablename__ = 'authors'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100))
    department: str = Column(String(5))

    schedules: List[Schedule] = relationship(
        'Schedule', back_populates='author'
    )

    def __init__(self, name: str, department: str = '') -> None:
        self.name = name
        self.department = department

    def __repr__(self) -> str:
        return f'<{self.name} ({self.department})>'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.name == other
        return False

    def __str__(self) -> str:
        return self.name


class Lesson(Base):
    __tablename__ = 'lessons'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(150))

    schedules: List[Schedule] = relationship(
        'Schedule', back_populates='lesson'
    )

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f'<Lesson {self.name}>'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.name == other
        return False


class LessonType(Base):
    __tablename__ = 'lesson_types'

    id: int = Column(Integer, primary_key=True)
    type: str = Column(String(30))

    def __init__(self, type: str) -> None:
        self.type = type

    def __repr__(self) -> str:
        return f'<Type {self.type}>'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.type == other
        return False


class Schedule(Base):
    __tablename__ = 'schedule'

    id: int = Column(Integer, primary_key=True)
    overline: bool = Column(Boolean)
    classroom: str = Column(String(30))
    corps: Optional[str] = Column(String(20), nullable=True)
    weekday: int = Column(Integer)  # 0..6
    num: int = Column(Integer)
    group_id: int = Column(Integer, ForeignKey('groups.id'))
    lesson_id: int = Column(Integer, ForeignKey('lessons.id'), nullable=False)
    author_id: int = Column(Integer, ForeignKey('authors.id'), nullable=True)
    lesson_type_id: int = Column(
        Integer, ForeignKey('lesson_types.id'), nullable=True
    )

    group: Group = relationship(
        'Group', back_populates='schedules', lazy='joined'
    )
    lesson: Lesson = relationship(
        'Lesson', back_populates='schedules', lazy='joined'
    )
    author: Optional[Author] = relationship(
        'Author', back_populates='schedules', lazy='joined'
    )
    lesson_type: Optional[LessonType] = relationship(
        'LessonType', lazy='joined'
    )

    def __init__(
        self,
        group: Union[Group, int],
        lesson: Union[Lesson, int],
        author: Union[Author, int],
        lesson_type: Union[LessonType, int],
        num: int,
        weekday: int,
        overline: bool,
        classroom: str,
        corps: Optional[str] = None,
    ) -> None:
        self.classroom = classroom
        if isinstance(group, Group):
            self.group = group
        else:
            self.group_id = group

        if isinstance(lesson, Lesson):
            self.lesson = lesson
        else:
            self.lesson_id = lesson

        if isinstance(author, Author):
            self.author = author
        else:
            self.author_id = author

        if isinstance(lesson_type, LessonType):
            self.lesson_type = lesson_type
        else:
            self.lesson_type_id = lesson_type

        self.num = num
        self.weekday = weekday
        self.overline = overline
        self.classroom = classroom
        self.corps = corps

    def __repr__(self) -> str:
        return f'<Schedule {"on line" if self.overline else "under line"} {self.classroom}>'

    def __str__(self) -> str:
        lesson_type = f'({self.lesson_type.type}) ' if self.lesson_type else ''
        author = f'{self.author.name} ' if self.author else ''
        classroom = self.classroom if self.classroom else ''
        lesson_time = Times.lesson_time(self.num)
        return f'{self.num}. {lesson_time[0]} - {lesson_time[1]}\n{self.lesson.name} {author}{lesson_type}{classroom}'

    def just_name(self) -> str:
        lesson_type = f'({self.lesson_type.type})' if self.lesson_type else ''
        classroom = self.classroom if self.classroom else ''
        return f'{self.lesson.name} {lesson_type} {classroom}'


class ActiveUser(Base):
    __tablename__ = 'active_users'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    tid: int = Column(BigInteger, unique=True, nullable=False)
    group_id: int = Column(Integer, ForeignKey('groups.id'), nullable=True)
    vip: bool = Column(Boolean, default=False)

    group: Optional[Group] = relationship('Group', lazy='joined')

    def __init__(self, tid: int, group: Union[Group, int, None] = None) -> None:
        self.tid = tid
        if isinstance(group, Group):
            self.group = group
        else:
            self.group_id = group

    def __repr__(self) -> str:
        return f'<User {self.tid}{(" [" + self.group.group + "]") if self.group is not None else ""}>'


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    logger.info('Database was initialized.')
