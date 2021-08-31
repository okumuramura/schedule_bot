from sqlalchemy import create_engine
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy import Table, Column
from sqlalchemy import Integer, Time, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from sqlalchemy import select


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
    Column("group", String, nullable=False)
)

lessons = Table("lessons", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String),
    Column("type", String(50)),
)

authors = Table("authors", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(50)),
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

    id = Column(Integer, primary_key=True)
    group = Column(String, nullable=False)
    schedules = relationship("Schedule", order_by=schedule.c.id, back_populates="group")

    def __init__(self, group : str):
        self.group = group

    def __repr__(self):
        return f"<Group {self.group}>"

    def __eq__(self, other):
        if type(other) == str:
            return self.group == other
        else:
            return False

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    schedules = relationship("Schedule", order_by=schedule.c.id, back_populates="author")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<{self.name}>"

    def __eq__(self, other):
        if type(other) == str:
            return self.name == other
        else:
            return False

    def __str__(self) -> str:
        return self.name

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    schedules = relationship("Schedule", back_populates="lesson")

    def __init__(self, name : str):
        self.name = name

    def __repr__(self):
        return f"<Lesson {self.name}>"

    def __eq__(self, other):
        if type(other) == str:
            return self.name == other
        else:
            return False

class LessonType(Base):
    __tablename__ = "lesson_types"

    id = Column(Integer, primary_key=True)
    type = Column(String(30))

    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return f"<Type {self.type}>"

    def __eq__(self, other):
        if type(other) == str:
            return self.type == other
        else:
            return False

class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True)
    on_line = Column(Boolean)
    classroom = Column(String(30))
    corps = Column(Integer, nullable=True)
    weekday = Column(Integer) # 0..6
    num = Column(Integer)
    group_id = Column(Integer, ForeignKey("groups.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"))
    lesson_type_id = Column(Integer, ForeignKey("lesson_types.id"))


    group = relationship("Group", back_populates="schedules")
    lesson = relationship("Lesson", back_populates="schedules")
    author = relationship("Author", back_populates="schedules")
    lesson_type = relationship("LessonType")


    def __init__(self, group, lesson, author, lesson_type, num, weekday, on_line, classroom, corps = None):
        self.classroom = classroom
        if corps is None:
            self.corps = self.try_get_corps(classroom)
        else:
            self.corps = corps
        
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
        return f"<Schedule {'on line' if self.on_line else 'under line'} {self.corps}-{self.classroom}>"

    def __str__(self) -> str:
        ltype = f"({self.lesson_type.type}) " if self.lesson_type else ""
        author = f"{self.author.name} " if self.author else ""
        classroom = self.classroom if self.classroom else ""
        return f"{self.num}. {self.lesson.name} {author}{ltype}{classroom}"

    def just_name(self) -> str:
        ltype = f"({self.lesson_type.type})" if self.lesson_type else ""
        return f"{self.lesson.name} {ltype}"

    def try_get_corps(self, classroom):
        return None

class ActiveUser(Base):
    __tablename__ = "active_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tid = Column(Integer, unique=True, nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"))
    state = Column(Integer, default=0)

    group = relationship("Group")

    def __init__(self, tid, group = None):
        self.tid = tid
        if type(group) == Group:
            self.group = group
        else:
            self.group_id = group

    def __repr__(self):
        return f"<User {self.tid}{(' [' + self.group.group + ']') if self.group is not None else ''} state: {self.state}>"



# engine = create_engine("sqlite:///lessons.db")
# metadata.create_all(engine)


if __name__ == "__main__":
    import json
    import os

    # if os.path.exists("lessons.db"):
    #     os.remove("lessons.db")

    engine = create_engine("sqlite:///lessons.db")
    metadata.create_all(engine)

    exit()

    with open("data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        _group_list = [Group(x) for x in data["groups"]]
        _lesson_list = [Lesson(x) for x in data["lessons"]]
        _lesson_types = [LessonType(x) for x in data["lesson_types"]]
        _author_list = [Author(x) for x in data["authors"]]

    _schedule = [
        Schedule(_group_list[0], _lesson_list[0], _author_list[0], 1, 1, Weekday.MONDAY, True, "3-240"),
        Schedule(_group_list[0], _lesson_list[1], _author_list[1], 2, 3, Weekday.MONDAY, True, "1-2")
    ]

    _users = [
        ActiveUser(12, 1),
        ActiveUser(231),
        ActiveUser(289518247, 1)
    ]

    session = Session(bind = engine)
    session.add_all(_group_list)
    session.add_all(_lesson_list)
    session.add_all(_lesson_types)
    session.add_all(_author_list)

    session.add_all(_schedule)
    session.add_all(_users)

    session.commit()

    labels = {
        "Groups": Group,
        "Lessons": Lesson,
        "Types": LessonType,
        "Authors": Author
    }

    print(session.query(ActiveUser).all())

    for label, cls in labels.items():
        print(label)
        for i in session.query(cls).all():
            print("  ", i)
        print()



