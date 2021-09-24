from manager import Manager
import db


class Updater:
    def __init__(self, db: str):
        self.manager = Manager(db)

    def clear_schedule(self):
        self.manager.session.execute(r"TRUNCATE TABLE `schedule`")
        self.manager.session.commit()

    def add_lessons(self, lessons_set):
        for l in lessons_set:
            l_id = self.manager.session.query(db.Lesson.id).filter(db.Lesson.name == l).first()
            if l_id is None:
                l_id = self.manager.add_lesson(l, commit=False)
        
        self.manager.session.commit()

    def add_authors(self, authors_set):
        for a in authors_set:
            a_id = self.manager.session.query(db.Author.id).filter(db.Author.name == a).first()
            if a_id is None:
                a_id = self.manager.add_author(a, commit=False)
        self.manager.session.commit()


    def add_group(self, group, schedule):
        g = self.manager.session.query(db.Group.id).filter(db.Group.group == group).first()
        if g is None:
            g = self.manager.add_group(group)
        else:
            g = g[0]

        weekday: int
        number: int
        is_overline: bool

        for i, lesson in enumerate(schedule):
            if lesson is None:
                continue
            l_id = self.manager.session.query(db.Lesson.id).filter(db.Lesson.name == lesson.name).first()
            if l_id is None:
                l_id = self.manager.add_lesson(lesson.name)
            else:
                l_id = l_id[0]
            weekday = i // 14
            is_overline = i % 2 == 0
            number = i % 14 // 2 + 1
            
            if lesson.author is not None:
                a_id = self.manager.session.query(db.Author.id).filter(db.Author.name == lesson.author).first()
                if a_id is None:
                    a_id = self.manager.add_author(lesson.author)
                else:
                    a_id = a_id[0]
            else:
                a_id = None

            if lesson.lesson_type is not None:
                t_id = self.manager.session.query(db.LessonType.id).filter(db.LessonType.type == lesson.lesson_type).first()
                if t_id is None:
                    print("No lesson type in db: " + lesson.lesson_type)
                else:
                    t_id = t_id[0]
            else:
                t_id = None

            self.manager.add_schedule(g, l_id, a_id, t_id, number, weekday, is_overline, lesson.auditory, commit=False)
        
        self.manager.session.commit()

            


        
        
