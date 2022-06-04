import sys
from typing import List

try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtWidgets, QtCore

import argparse

from schedule_bot.manager import Manager


class LessonHeader(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.label = QtWidgets.QLabel()
        self.lesson = QtWidgets.QLabel()
        self.author = QtWidgets.QLabel()
        self.type = QtWidgets.QLabel()
        self.auditory = QtWidgets.QLabel()

        self.label.setText("№")
        self.label.setFixedWidth(30)
        self.lesson.setText("Предмет")
        self.author.setText("Преподаватель")
        self.type.setText("Тип")
        self.auditory.setText("Аудитория")

        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.lesson.setAlignment(QtCore.Qt.AlignCenter)
        self.author.setAlignment(QtCore.Qt.AlignCenter)
        self.type.setAlignment(QtCore.Qt.AlignCenter)
        self.auditory.setAlignment(QtCore.Qt.AlignCenter)

        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.label)
        self.hlayout.addWidget(self.lesson)
        self.hlayout.addWidget(self.author)
        self.hlayout.addWidget(self.type)
        self.hlayout.addWidget(self.auditory)
        self.hlayout.addSpacing(40)

        self.setLayout(self.hlayout)


class LessonRow(QtWidgets.QWidget):
    removed = QtCore.Signal(int)

    def __init__(self, id, parent=None):
        super().__init__()
        self._parent = parent
        self.id = id
        self.hlayout = QtWidgets.QHBoxLayout()

        self.label = QtWidgets.QLabel()
        self.label.setText(str(id))
        self.label.setMinimumWidth(30)

        self.lesson = QtWidgets.QComboBox()
        self.author = QtWidgets.QComboBox()
        self.type = QtWidgets.QComboBox()
        self.lesson.setEditable(True)
        self.author.setEditable(True)

        self.auditory = QtWidgets.QLineEdit()

        self.remove_btn = QtWidgets.QPushButton()
        self.remove_btn.clicked.connect(self.remove)
        self.remove_btn.setText("x")
        self.remove_btn.setFixedWidth(20)
        self.remove_btn.setFixedHeight(20)
        self.remove_btn.setStyleSheet("background: rgba(255, 0, 0, 90)")

        self.hlayout.addWidget(self.label)
        self.hlayout.addWidget(self.lesson)
        self.hlayout.addWidget(self.author)
        self.hlayout.addWidget(self.type)
        self.hlayout.addWidget(self.auditory)
        self.hlayout.addWidget(self.remove_btn)
        self.setLayout(self.hlayout)

    def is_empty(self) -> bool:
        return not self.lesson.currentText()

    def clear(self):
        self.lesson.setCurrentText("")
        self.author.setCurrentText("")
        self.type.setCurrentText("")
        self.auditory.setText("")

    def remove(self):
        self.clear()
        self._parent.remove_row(self.id)


class LessonTable(QtWidgets.QWidget):
    row_removed = QtCore.Signal(int)

    def __init__(self, data, lesson_quantity=10):
        super().__init__()
        self.lessons_quantity = lesson_quantity

        self.groups = data["groups"]
        self.lessons = data["lessons"]
        self.types = data["types"]
        self.authors = data["authors"]

        self.group_names = [""] + [x.group for x in self.groups]
        self.lesson_names = [""] + [x.name for x in self.lessons]
        self.type_names = [""] + [x.type for x in self.types]
        self.author_names = [""] + [x.name for x in self.authors]

        self.vlayout = QtWidgets.QVBoxLayout()
        self.lesson_rows = []
        for i in range(self.lessons_quantity):
            lesson = LessonRow(i + 1, self)
            lesson.lesson.addItems(self.lesson_names)
            lesson.author.addItems(self.author_names)
            lesson.type.addItems(self.type_names)
            self.lesson_rows.append(lesson)
            if i == 0:
                self.header = LessonHeader()
                self.header.lesson.setMinimumWidth(
                    lesson.lesson.minimumSizeHint().width()
                )
                self.header.author.setMinimumWidth(
                    lesson.author.minimumSizeHint().width()
                )
                self.header.type.setMinimumWidth(
                    lesson.type.minimumSizeHint().width()
                )
                self.header.auditory.setMinimumWidth(
                    lesson.auditory.minimumWidth()
                )
                self.vlayout.addWidget(self.header)
            self.vlayout.addWidget(lesson)

        self.setLayout(self.vlayout)

    def update_data(self, data):
        for row in self.lesson_rows:
            row.clear()

        for sch, lesson, author, tp in data:
            row: LessonRow
            row = self.lesson_rows[sch.num - 1]
            row.lesson.setCurrentText(lesson.name)
            if author is not None:
                row.author.setCurrentText(author.name)
            if tp is not None:
                row.type.setCurrentText(tp.type)
            if sch.classroom:
                row.auditory.setText(sch.classroom)

    def update_items(self, data) -> None:
        self.groups: List[database.Group] = data["groups"]
        self.lessons: List[database.Lesson] = data["lessons"]
        self.types: List[database.LessonType] = data["types"]
        self.authors: List[database.Author] = data["authors"]

        self.group_names: List[str] = [""] + [x.group for x in self.groups]
        self.lesson_names: List[str] = [""] + [x.name for x in self.lessons]
        self.type_names: List[str] = [""] + [x.type for x in self.types]
        self.author_names: List[str] = [""] + [x.name for x in self.authors]

        row: LessonRow
        for row in self.lesson_rows:
            lstr = row.lesson.currentText()
            astr = row.author.currentText()
            row.lesson.clear()
            row.author.clear()
            row.lesson.addItems(self.lesson_names)
            row.author.addItems(self.author_names)
            row.lesson.setCurrentText(lstr)
            row.author.setCurrentText(astr)

    def remove_row(self, id: int) -> None:
        self.row_removed.emit(id)


class MainWindow(QtWidgets.QWidget):
    WEEKDAYS = {
        "Понедельник": 0,
        "Вторник": 1,
        "Среда": 2,
        "Четверг": 3,
        "Пятница": 4,
        "Суббота": 5,
    }

    def __init__(self, _db: str) -> None:
        super().__init__()
        self.manager = Manager(_db)
        self.prepare_data()
        self.prepare_table()

        self.main_layout = QtWidgets.QVBoxLayout()
        self.dialog_layout = QtWidgets.QHBoxLayout()

        self.group_dialog = QtWidgets.QInputDialog()
        self.group_dialog.setComboBoxItems(self.group_names)
        self.group_dialog.setComboBoxEditable(True)
        self.group_dialog.setOption(QtWidgets.QInputDialog.NoButtons, True)
        self.group_dialog.setLabelText("Группа")

        self.weekday_dialog = QtWidgets.QInputDialog()
        self.weekday_dialog.setComboBoxItems(self.WEEKDAYS.keys())
        self.weekday_dialog.setComboBoxEditable(False)
        self.weekday_dialog.setOption(QtWidgets.QInputDialog.NoButtons, True)
        self.weekday_dialog.setLabelText("День")

        self.on_line = QtWidgets.QCheckBox()
        self.on_line.setText("Над чертой")
        self.on_line.setChecked(True)

        self.submit_btn = QtWidgets.QPushButton()
        self.submit_btn.setText("Применить")
        self.submit_btn.setMaximumWidth(250)
        self.submit_btn.clicked.connect(self.submit_input)

        self.save_btn = QtWidgets.QPushButton()
        self.save_btn.setText("Сохранить")
        self.save_btn.setMaximumWidth(250)
        self.save_btn.clicked.connect(self.save_input)

        self.dialog_layout.addWidget(self.group_dialog)
        self.dialog_layout.addWidget(self.weekday_dialog)
        self.dialog_layout.addWidget(self.on_line)

        self.main_layout.addLayout(self.dialog_layout)
        self.main_layout.addWidget(self.submit_btn, 0, QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.save_btn)

        self.setLayout(self.main_layout)

    def prepare_data(self):
        self.data = self.manager.get_data()
        self.groups: List[database.Group] = self.data["groups"]
        self.lessons: List[database.Lesson] = self.data["lessons"]
        self.authors: List[database.Author] = self.data["authors"]
        self.types: List[database.LessonType] = self.data["types"]

        self.group_names: List[str] = [x.group for x in self.groups]

    def prepare_table(self):
        self.scroll_area = QtWidgets.QScrollArea()
        self.lesson_table = LessonTable(self.data, 10)
        self.scroll_area.setWidget(self.lesson_table)
        self.lesson_table.setEnabled(False)
        self.lesson_table.row_removed.connect(self.remove_lesson)

    def submit_input(self):
        weekday = self.weekday_dialog.textValue()
        group = self.group_dialog.textValue()
        if group not in self.groups:
            self.manager.add_group(group)
            self.groups = self.manager.get_groups()
            self.group_names.append(group)
            self.group_dialog.setComboBoxItems(self.group_names)
            self.group_dialog.setTextValue(group)

        self.lesson_table.setEnabled(True)
        self.lessons_data = self.manager.get_schedule(
            group, self.day2int(weekday), self.on_line.isChecked()
        )
        self.lesson_table.update_data(self.lessons_data)

    def save_input(self):
        row: LessonRow
        new_data = False
        for row in self.lesson_table.lesson_rows:
            if not row.is_empty():
                num = row.id

                lstr = row.lesson.currentText()
                if lstr in self.lessons:
                    lid = self.lessons.index(lstr) + 1
                else:
                    lid = self.manager.add_lesson(lstr)
                    new_data = True

                astr = row.author.currentText()
                if astr == "":
                    aid = None
                elif astr in self.authors:
                    aid = self.authors.index(astr) + 1
                else:
                    aid = self.manager.add_author(astr)
                    new_data = True

                auditory = row.auditory.text()
                if not auditory:
                    auditory = None

                gstr = self.group_dialog.textValue()
                gid = self.groups.index(gstr) + 1

                is_overline = self.on_line.isChecked()
                weekday = self.day2int(self.weekday_dialog.textValue())

                if row.type.currentText():
                    ltype = self.types.index(row.type.currentText()) + 1
                else:
                    ltype = None

                # self.manager.add_schedule(gid, lid, aid, ltype, num, weekday, is_overline, auditory)
                _ = self.manager.add_or_upd_schedule(
                    gid, lid, aid, ltype, num, weekday, is_overline, auditory
                )
                if new_data:
                    self.prepare_data()
                    self.lesson_table.update_items(self.data)

    def day2int(self, weekday: str) -> int:
        return self.WEEKDAYS.get(weekday, -1)

    @QtCore.Slot(int)
    def remove_lesson(self, id: int) -> None:
        gstr = self.group_dialog.textValue()
        gid = self.groups.index(gstr) + 1

        is_overline = self.on_line.isChecked()

        weekday = self.day2int(self.weekday_dialog.textValue())

        self.manager.delete_schedule(gid, weekday, is_overline, id)


if __name__ == "__main__":
    DEFAULT_DB = "sqlite://lessons.db"
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "-b",
        "--db",
        action="store",
        dest="db",
        type=str,
        default=DEFAULT_DB,
        help="database url (%s by default)" % DEFAULT_DB,
    )

    args = argument_parser.parse_args()
    database = args.db

    app = QtWidgets.QApplication([])

    window = MainWindow(database)
    window.show()

    sys.exit(app.exec_())
