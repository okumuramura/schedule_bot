import argparse
from typing import Any, List, Optional, Union

from sqlalchemy import (Boolean, Column, ForeignKey, Integer, MetaData, String,
                        Table, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

from schedule_bot.times import Times

metadata = MetaData()
Base = declarative_base()

class Weekday:
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

groups = Table("groups", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("group", String(20), nullable=False)
)

lessons = Table("lessons", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(200)),
    Column("type", String(50)),
)

authors = Table("authors", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100)),
    Column("department", String(5))
)

schedule = Table("schedule", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("on_line", Boolean),
    Column("classroom", String(30)),
    Column("corps", Integer, nullable=True),
    Column("weekday", Integer),
    Column("num", Integer),
    Column("group_id", Integer, ForeignKey("groups.id")),
    Column("lesson_id", Integer, ForeignKey("lessons.id"), nullable=False),
    Column("author_id", Integer, ForeignKey("authors.id")),
    Column("lesson_type_id", Integer, ForeignKey("lesson_types.id"))
)

lesson_types = Table("lesson_types", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("type", String(30))
)

active_users = Table("active_users", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("tid", Integer, unique=True, nullable=False),
    Column("group_id", Integer, ForeignKey("groups.id")),
    Column("state", Integer, default=0)
)

class Group(Base):
    __tablename__ = "groups"

    id: int = Column(Integer, primary_key=True)
    group: str = Column(String(20), nullable=False)
    schedules = relationship("Schedule", order_by=schedule.c.id, back_populates="group")

    def __init__(self, group : str) -> None:
        self.group = group

    def __repr__(self) -> str:
        return f"<Group {self.group}>"

    def __str__(self) -> str:
        return self.group

    def __eq__(self, other: Any) -> bool:
        if type(other) == str:
            return self.group == other
        else:
            return False

class Author(Base):
    __tablename__ = "authors"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100))
    department: str = Column(String(5))

    schedules = relationship("Schedule", order_by=schedule.c.id, back_populates="author")

    def __init__(self, name: str, department: str = "") -> None:
        self.name = name
        self.department = department

    def __repr__(self) -> str:
        return f"<{self.name} ({self.department})>"

    def __eq__(self, other: Any) -> bool:
        if type(other) == str:
            return self.name == other
        else:
            return False

    def __str__(self) -> str:
        return self.name

class Lesson(Base):
    __tablename__ = "lessons"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(150))

    schedules = relationship("Schedule", back_populates="lesson")

    def __init__(self, name : str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"<Lesson {self.name}>"

    def __eq__(self, other: Any) -> bool:
        if type(other) == str:
            return self.name == other
        else:
            return False

class LessonType(Base):
    __tablename__ = "lesson_types"

    id: int = Column(Integer, primary_key=True)
    type: str = Column(String(30))

    def __init__(self, type: str) -> None:
        self.type = type

    def __repr__(self) -> str:
        return f"<Type {self.type}>"

    def __eq__(self, other: Any) -> bool:
        if type(other) == str:
            return self.type == other
        else:
            return False

class Schedule(Base):
    __tablename__ = "schedule"

    id: int = Column(Integer, primary_key=True)
    on_line: bool = Column(Boolean)
    classroom: str = Column(String(30))
    corps: int = Column(Integer, nullable=True)
    weekday: int = Column(Integer) # 0..6
    num: int = Column(Integer)
    group_id: int = Column(Integer, ForeignKey("groups.id"))
    lesson_id: int = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    author_id: int = Column(Integer, ForeignKey("authors.id"))
    lesson_type_id: int = Column(Integer, ForeignKey("lesson_types.id"))


    group = relationship("Group", back_populates="schedules")
    lesson = relationship("Lesson", back_populates="schedules")
    author = relationship("Author", back_populates="schedules")
    lesson_type = relationship("LessonType")


    def __init__(self, group: Union[Group, int], 
                        lesson: Union[Lesson, int], 
                        author: Union[Author, int], 
                        lesson_type: Union[LessonType, int], 
                        num: int, 
                        weekday: int, 
                        on_line: bool, 
                        classroom: str, 
                        corps: Optional[str] = None) -> None:
        self.classroom = classroom
        if type(group) == Group:
            self.group = group
        else:
            self.group_id = group

        if type(lesson) == Lesson:
            self.lesson = lesson
        else:
            self.lesson_id = lesson

        if type(author) == Author:
            self.author = author
        else:
            self.author_id = author

        if type(lesson_type) == LessonType:
            self.lesson_type = lesson_type
        else:
            self.lesson_type_id = lesson_type

        self.num = num
        self.weekday = weekday
        self.on_line = on_line
        self.classroom = classroom
        self.corps = corps

    def __repr__(self):
        return f"<Schedule {'on line' if self.on_line else 'under line'} {self.classroom}>"

    def __str__(self) -> str:
        ltype = f"({self.lesson_type.type}) " if self.lesson_type else ""
        author = f"{self.author.name} " if self.author else ""
        classroom = self.classroom if self.classroom else ""
        lesson_time = Times.lesson_time(self.num)
        return f"{self.num}. {lesson_time[0]} - {lesson_time[1]}\n{self.lesson.name} {author}{ltype}{classroom}"

    def just_name(self) -> str:
        ltype = f"({self.lesson_type.type})" if self.lesson_type else ""
        classroom = self.classroom if self.classroom else ""
        return f"{self.lesson.name} {ltype} {classroom}"

class ActiveUser(Base):
    __tablename__ = "active_users"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    tid: int = Column(Integer, unique=True, nullable=False)
    group_id: int = Column(Integer, ForeignKey("groups.id"))
    state: int = Column(Integer, default=0)

    group = relationship("Group")

    def __init__(self, tid: int, group: Union[Group, int, None] = None) -> None:
        self.tid = tid
        if type(group) == Group:
            self.group = group
        else:
            self.group_id = group

    def __repr__(self) -> str:
        return f"<User {self.tid}{(' [' + self.group.group + ']') if self.group is not None else ''} state: {self.state}>"



if __name__ == "__main__":
    DEFAULT_DB = "sqlite://lessons.db"
    
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-i", "--init", 
        action="store_true", 
        dest="init", 
        help = "init database (create tables)"
    )
    argument_parser.add_argument("-b", "--db", 
        action="store", 
        dest="db", 
        type = str, 
        default=DEFAULT_DB, 
        help = "database URL (%s by default)" % DEFAULT_DB
    )

    args = argument_parser.parse_args()
    db_url = args.db
    init = args.init

    if init:
        print("connecting to %s" % db_url)
        engine = create_engine(db_url, echo = True, encoding="utf-8")
        metadata.create_all(engine)

        lesson_types_str = [
            "лек", "практ", "лаб", "лек+практ", "практ+лаб", "лек+лаб", "практ+лек", "лаб+практ", "лаб+лек"
        ]

        lesson_types = [LessonType(l) for l in lesson_types_str]

        session = Session(bind = engine)
        session.add_all(lesson_types)
        session.commit()
        print("Database initialized!")
