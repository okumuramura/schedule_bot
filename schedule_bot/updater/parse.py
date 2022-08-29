from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional, Set, Union

import colorama
import numpy as np
import xlrd

from schedule_bot.updater import Updater, regexp
from schedule_bot.updater.arguments import argument_parser


class Lesson:
    def __init__(
        self,
        name: str,
        author: Optional[str] = None,
        auditory: Optional[str] = None,
        lesson_type: Optional[str] = None,
        department: Optional[str] = None,
        raw: str = '',
    ) -> None:
        self.name = name
        self.author = author
        self.auditory = auditory
        self.lesson_type = lesson_type
        self.department = department
        self.raw = raw

    def is_full(self) -> bool:
        return self.is_pe() or not (
            self.name is None
            or self.department is None
            or self.author is None
            or self.auditory is None
            or self.lesson_type is None
        )

    def is_pe(self) -> bool:
        return (
            self.name is not None and self.name == 'Физическая культура и спорт'
        )

    def __eq__(self, other: Union[Lesson, Any]) -> bool:
        return all(
            (
                isinstance(other, Lesson),
                self.name == other.name,
                self.author == other.author,
                self.auditory == other.auditory,
                self.lesson_type == other.lesson_type,
                self.department == other.department,
            )
        )

    def __str__(self) -> str:
        if not self.is_full():
            return f'{colorama.Fore.RED}{str(self.department):^5}|{self.lesson_type.__str__():^16}|{str(self.name):^120}|{str(self.author):^25}|{str(self.auditory):^8} {colorama.Fore.BLUE}{self.raw:^120}{colorama.Fore.RESET}'
        return f'{str(self.department):^5}|{self.lesson_type.__str__():^16}|{str(self.name):^120}|{str(self.author):^25}|{str(self.auditory):^8} {colorama.Fore.BLUE}{self.raw:^120}{colorama.Fore.RESET}'

    def __repr__(self) -> str:
        return f'Lesson({str(self.department)}, {str(self.lesson_type)}, {str(self.name)}, {str(self.author)}, {str(self.auditory)})'


class Counter:
    errors: int = 0
    passed: int = 0
    incomplete: int = 0
    total: int = 0
    unnamed: int = 0

    def __str__(self) -> str:
        return 'Total: {0}\n{5}Incomplete: {1}{8}\n{6}Passed: {2}{8}\n{7}Unnamed: {3}{8}\n{7}Errors: {4}{8}'.format(
            self.total,
            self.incomplete,
            self.passed,
            self.unnamed,
            self.errors,
            colorama.Fore.YELLOW,
            colorama.Fore.GREEN,
            colorama.Fore.RED,
            colorama.Fore.RESET,
        )


def normalize_name(name: str, start_pos: Optional[int] = None) -> str:
    sp = start_pos is not None
    LONG_NAMES = ['аль аккад мхд айман']

    if name.lower() in LONG_NAMES:
        if sp:
            return name, start_pos
        return name

    names: List[str] = re.findall(r"\w+", name)
    if len(names) > 3:
        if sp:
            start_pos += len(" ".join(names)) - len(" ".join(names[-3:]))
        names = names[-3:]

    if sp:
        return (
            f"{names[0].capitalize()} {names[1][0]}.{names[2][0]}.",
            start_pos,
        )
    return f"{names[0].capitalize()} {names[1][0]}.{names[2][0]}."


def normalize_auditory(s: str) -> str:
    s = s.strip()
    if re.search("ижводоканал", s, re.IGNORECASE) is not None:
        return "МУП «Ижводоканал»"
    f = re.search(r"ООО\s?(?P<name>[«\"][\w-]+[»\"])", s, re.IGNORECASE)
    if f is not None:
        return f"ООО {f.group('name')}"
    if re.search(r"ЭОиДОТ", s, re.IGNORECASE) is not None:
        return "ЭОиДОТ"
    if re.search(r"ИжНТ", s, re.IGNORECASE) is not None:
        return "ИжНТ"

    s = re.sub(r"(\s)|(к.)|(К.)", "", s)
    return s


def normalize_lesson_type(s: str) -> str:
    s = s.strip()
    types = s.split("+")
    final_type = []
    for tp in types:
        if re.search(r"(леке?ц?и?я?\.*)", tp, re.IGNORECASE) is not None:
            final_type.append("лек")
        elif re.search(r"(практ?и?к?а?\.*)", tp, re.IGNORECASE) is not None:
            final_type.append("практ")
        else:
            final_type.append("лаб")

    return "+".join(final_type)


def parse_lesson_exp(lesson_line: str) -> Lesson:
    lesson_line = lesson_line.replace("\n", " ")
    raw_line = lesson_line

    authorname_re = re.compile(regexp.AUTHOR)
    department_re = re.compile(regexp.DEPARTMENT)
    classroom_re = re.compile(regexp.CLASSROOM, re.IGNORECASE)
    lesson_type_re = re.compile(regexp.LESSON_TYPE, re.IGNORECASE)
    lesson_re = re.compile(regexp.LESSON)
    lesson_re_no_author = re.compile(regexp.LESSON_NO_AUTHOR)

    delta = 0
    author_group = authorname_re.search(lesson_line)
    if author_group is not None:
        asp = author_group.span("ath")[0]
        g = author_group.group(0)
        t = re.search(r"^(?P<t>\s*((пр\.)|(доц\.)|(проф\.))\s*)", g)
        if t is not None:
            delta = len(t.group("t"))

        author = author_group.group("ath")
        author = author.rstrip()

    department_group = department_re.search(lesson_line)
    if department_group is not None:
        department = department_group.group("dep")
        lesson_line = lesson_line.replace(department, '*' * len(department), 1)

    auditory_group = classroom_re.search(lesson_line)
    if auditory_group is not None:
        auditory = normalize_auditory(auditory_group.group(0))

    lesson_type_group = lesson_type_re.search(lesson_line)
    if lesson_type_group is not None:
        lesson_type = normalize_lesson_type(lesson_type_group.group("type"))

    # find author substring's start position
    if author is not None:
        author, author_start_pos = normalize_name(author, asp)
        author_start_pos -= delta
    else:
        author_start_pos = len(lesson_line)

    if author is None:
        lesson_name_group = lesson_re_no_author.search(lesson_line)
    else:
        lesson_name_group = lesson_re.search(lesson_line, endpos=author_start_pos)
    if lesson_name_group is not None:
        lesson_name = lesson_name_group.group("name").strip(", ")

    return Lesson(
        lesson_name,
        author=author,
        department=department,
        raw=raw_line,
        auditory=auditory,
        lesson_type=lesson_type,
    )


PREFIX = 0


def parse_table(tablename: str) -> Dict[str, np.ndarray]:
    global PREFIX
    data = xlrd.open_workbook(tablename, formatting_info=True)
    mats = {}

    for sheet_id in range(data.nsheets):
        sheet = data.sheet_by_index(sheet_id)

        mat: np.ndarray = np.empty((sheet.ncols, sheet.nrows), object)

        merged_cells = sheet.merged_cells

        for ncol in range(sheet.ncols):
            for nrow in range(sheet.nrows):
                mat[ncol][nrow] = sheet[nrow][ncol].value

        for (x0, x1, y0, y1) in merged_cells:
            cell_data = sheet[x0][y0].value
            for x in range(x0, x1):
                for y in range(y0, y1):
                    mat[y][x] = cell_data

        mats.update({sheet.name + str(PREFIX): mat})
        PREFIX += 1
    return mats


def parse_sheet(sheet: np.ndarray) -> Dict[str, List[Optional[Lesson]]]:
    global SHOW
    global PROGRESS

    global LESSONS_SET
    global AUTHORS_SET

    lessons = {}
    cols, rows = sheet.shape
    GROUP_REGEX = re.compile(regexp.GROUP)

    for x in range(cols):
        for y in range(rows):
            if GROUP_REGEX.match(sheet[x][y]) is not None:
                group = sheet[x][y].split("\n")[0]

                logging.debug("GROUP: %s", group)
                ls = []
                for d in range(1, 85):
                    lesson = sheet[x][y + d]
                    if lesson.strip() != "":
                        COUNTER.total += 1
                        try:
                            lesson_info = parse_lesson_exp(sheet[x][y + d])

                            if lesson_info is not None:
                                if lesson_info.name is not None:
                                    LESSONS_SET.add(lesson_info.name)
                                if lesson_info.author is not None:
                                    AUTHORS_SET.add(lesson_info.author)

                                if SHOW == "ALL":
                                    if PROGRESS:
                                        tqdm.write(lesson_info.__str__())
                                    else:
                                        print(lesson_info)
                                if not lesson_info.is_full():
                                    if SHOW == "INCOMPLETE":
                                        if PROGRESS:
                                            tqdm.write(lesson_info.__str__())
                                        else:
                                            print(lesson_info)
                                    COUNTER.incomplete += 1
                                if lesson_info.name is None:
                                    COUNTER.unnamed += 1
                            ls.append(lesson_info)
                            COUNTER.passed += 1
                        except AttributeError:
                            logging.error(lesson.replace("\n", " "))
                            COUNTER.errors += 1

                    else:
                        ls.append(None)
                lessons.update({group: ls})

    return lessons


colorama.init(convert=True)


COUNTER = Counter()
SHOW = "ALL"
PROGRESS = True

LESSONS_SET: Set[str] = set()
AUTHORS_SET: Set[str] = set()

try:
    from tqdm import tqdm
except ImportError:
    PROGRESS = False

if __name__ == "__main__":
    args = argument_parser.parse_args()

    SHOW = args.show
    db_url: str = args.db
    filedir: str = args.dir
    DEBUG: bool = args.debug

    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)

    lessons: Dict[str, List[Optional[Lesson]]] = {}
    files: List[str] = []

    for file in os.listdir(filedir):
        ext = file.split(".")[-1]
        if ext == "xls":
            logging.debug("Added %s", file)
            files.append(os.path.join(filedir, file))
        else:
            logging.debug("Skiped %s", file)

    if PROGRESS:
        files = tqdm(files, position=0, leave=True, desc="files")

    for table in files:
        logging.debug("Parsing file: %s", table)
        sheets = parse_table(table)
        for sheet_name, sheet in sheets.items():
            logging.debug("\tSHEET: %s", sheet_name)
            group_schedule = parse_sheet(sheet)
            lessons.update(group_schedule)

    logging.info(str(COUNTER))

    is_updating: str = input("Put data into database (%s)? [y/n]: " % db_url)
    if is_updating.lower() == "y":
        upd = Updater()
        upd.clear_schedule()
        print("Adding lessons list: ", end="")
        upd.add_lessons(LESSONS_SET)
        print("OK")
        print("Adding authors list: ", end="")
        upd.add_authors(AUTHORS_SET)
        print("OK")

        if PROGRESS:
            lessons_list = tqdm(lessons.items())
        else:
            lessons_list = lessons.items()

        for group, sch in lessons_list:
            upd.add_group(group, sch)
    else:
        logging.info('abort')
