import argparse
import logging
import os
import re
from typing import Dict, List, Optional, Set

import colorama
import numpy as np
import xlrd

from schedule_bot.updater import Updater


class Lesson:
    def __init__(self, 
                name: str, 
                author: str = None, 
                auditory: str = None, 
                lesson_type: str = None,
                department: str = None,
                raw: str = None) -> None:
        self.name: str = name
        self.author: str = author
        self.auditory: str = auditory
        self.lesson_type: str = lesson_type
        self.department: str = department
        self.raw: str = raw

    def is_full(self) -> bool:
        return self.is_pe() or not (
            self.name is None or
            self.department is None or
            self.author is None or
            self.auditory is None or
            self.lesson_type is None
        )

    def is_pe(self) -> bool:
        return self.name is not None and self.name == "Физическая культура и спорт"

    def __eq__(self, o) -> bool:
        return (type(o) == type(self) and
            self.name == o.name and
            self.author == o.author and
            self.auditory == o.auditory and
            self.lesson_type == o.lesson_type and
            self.department == o.department
            )

    def __str__(self) -> str:
        if not self.is_full():
            return f"{colorama.Fore.RED}{str(self.department):^5}|{self.lesson_type.__str__():^16}|{str(self.name):^120}|{str(self.author):^25}|{str(self.auditory):^8} {colorama.Fore.BLUE}{self.raw:^120}{colorama.Fore.RESET}"
        return f"{str(self.department):^5}|{self.lesson_type.__str__():^16}|{str(self.name):^120}|{str(self.author):^25}|{str(self.auditory):^8} {colorama.Fore.BLUE}{self.raw:^120}{colorama.Fore.RESET}"
        #return f"({self.department})({self.lesson_type}) {self.name} - {self.author} {self.auditory}"
        

def parse_lesson_exp(lesson_line: str) -> Lesson:

    def short_name(s: str, start_pos: Optional[int] = None) -> str:
        sp = start_pos is not None
        LONG_NAMES = [
            "Аль Аккад Мхд Айман"
        ]
        
        if s in LONG_NAMES:
            if sp:
                return s, start_pos
            return s

        names = re.findall(r"\w+", s)
        if len(names) > 3:
            if sp:
                start_pos += len(" ".join(names)) - len(" ".join(names[-3:]))
            names = names[-3:]
            
        if sp:
            return f"{names[0].capitalize()} {names[1][0]}.{names[2][0]}.", start_pos
        return f"{names[0].capitalize()} {names[1][0]}.{names[2][0]}."

    def format_auditory(s: str) -> str:
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

        s = re.sub("(\s)|(к.)|(К.)", "", s)
        return s

    def format_type(s: str) -> str:
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


    lesson_line = lesson_line.replace("\n", " ")
    #author_name = re.compile(r"[А-Я][а-я]+\s([А-Я](([а-я]+)|\.)\s?)+[А-Я]([а-я]+)?\.?")
    authorname_re = re.compile(r"(((пр\.)|(доц\.)|(проф\.))\s*)?(?P<ath>([А-ЯЁ][А-Яа-яё]+(\s|\.)+(\s|\.)?[А-ЯЁ](\s|\.)+(\s|\.)?[А-ЯЁ]\.?)|(([А-ЯЁ][а-яё]+\s?){3,}))")
    department_re = re.compile(r"^\s*\(?(?P<dep>\d+\w?)\)?")
    classroom_re = re.compile(r"((БИ|(\d(к.)?))\w?\s?-(ОД-)?\s?\d+\w?\d?((/\d[^\-/]*)|(\-[\d\w]+))?)|(ЭОиДОТ)|(ООО\s?[«\"][\w-]+[»\"])|(ижводоканал)|(ИжНТ)", re.IGNORECASE)
    lesson_type_re = re.compile(r"[\(\s](?P<type>((леке?ц?и?я?\.*)?\s?\+?\s?(практ?и?к?а?\.*)?\s?\+?\s?((л[/\.]\s?р?\.*)|(лаб\.*))?\s?\+?\s?(практ?и?к?а?\.*)?\s?\+?\s?(леке?ц?и?я?\.*)?))(\s\d(,\s?\d)?\sп/гр)?[\)\s]", re.IGNORECASE)
    lesson_re = re.compile(r"\s*((\(?[\w\s/+\.,-]+\)\s*)|(\([\w\s/+\.,-]+\)?\s*))*(?P<name>[\w\sё\.,-]{3,})(\s*(\([\w\s/+\.,-]+\)\s*))*(,\s*)?")
    lesson_re_no_author = re.compile(r"\s*(\(?[\w\s/+\.,-]+\)\s*)*(?P<name>[\w\sё\.-]{3,})(\s*(\([\w\s/+\.,-]+\)\s*))*(,\s*)?")
    delta = 0
    author = authorname_re.search(lesson_line)
    if author is not None:
        asp = author.span("ath")[0]
        g = author.group(0)
        t = re.search(r"^(?P<t>\s*((пр\.)|(доц\.)|(проф\.))\s*)", g)
        if t is not None:
            delta = len(t.group("t"))
            
        author = author.group("ath")
        author = author.rstrip()
        
        
    department = department_re.search(lesson_line)
    if department is not None:
        department = department.group("dep")
    
    auditory = classroom_re.search(lesson_line)
    if auditory is not None:
        auditory = format_auditory(auditory.group(0))
    
    lesson_type = lesson_type_re.search(lesson_line)
    if lesson_type is not None:
        lesson_type = format_type(lesson_type.group("type"))

    # find author substring's start position
    if author is not None:
        author, author_start_pos = short_name(author, asp)
        author_start_pos -= delta
    else:
        author_start_pos = len(lesson_line)

    if author is None:
        lesson_name = lesson_re_no_author.search(lesson_line)
    else:
        lesson_name = lesson_re.search(lesson_line, endpos=author_start_pos)
    if lesson_name is not None:
        lesson_name = lesson_name.group("name").strip(", ")

    
    return Lesson(
        lesson_name,
        author = author,
        department = department,
        raw = lesson_line,
        auditory = auditory,
        lesson_type = lesson_type
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
    global ERRORS
    global PASSED
    global TOTAL
    global INCOMPLETE
    global SHOW
    global UNNAMED
    global PROGRESS

    global LESSONS_SET
    global AUTHORS_SET

    lessons = {}
    COLS, ROWS = sheet.shape
    GROUP_REGEX = re.compile(r"[А-Я]\d\d-\d\d\d-\d")
    for x in range(COLS):
        for y in range(ROWS):
            if GROUP_REGEX.match(sheet[x][y]) is not None:
                group = sheet[x][y].split("\n")[0]

                logging.debug("GROUP: " + group)
                ls = []
                for d in range(1, 85):
                    lesson = sheet[x][y+d]
                    if lesson.strip() != "":
                        TOTAL += 1
                        try:
                            l = parse_lesson_exp(sheet[x][y+d])

                            if l is not None:
                                if l.name is not None:
                                    LESSONS_SET.add(l.name)
                                if l.author is not None:
                                    AUTHORS_SET.add(l.author)
                                
                                if SHOW == "ALL":
                                    if PROGRESS:
                                        if l.auditory == "2-134/2":
                                            tqdm.write(l.__str__())
                                    else:
                                        print(l)
                                if not l.is_full():
                                    if SHOW == "INCOMPLETE":
                                        if PROGRESS:
                                            tqdm.write(l.__str__())
                                        else:
                                            print(l)
                                    INCOMPLETE += 1
                                if l.name is None:
                                    UNNAMED += 1
                            ls.append(l)
                            PASSED += 1
                        except AttributeError:
                            logging.error(lesson.replace("\n", " "))
                            ERRORS += 1
                            
                    else:
                        ls.append(None)
                lessons.update({group: ls})
    
    return lessons
    

colorama.init(convert=True)


PASSED = 0
ERRORS = 0
INCOMPLETE = 0
UNNAMED = 0
TOTAL = 0
SHOW = "ALL"
PROGRESS = True

LESSONS_SET: Set[str] = set()
AUTHORS_SET: Set[str] = set()

try:
    from tqdm import tqdm
except ImportError:
    PROGRESS = False

if __name__ == "__main__":
    DEFAULT_DB = "sqlite://lessons.db"

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-d", "--dir", dest="dir", action="store", type=str, default="./", help="directory with files")
    argument_parser.add_argument("-a", "--all", dest="show", action="store_const", const="ALL", default="NO", help = "show all lessons")
    argument_parser.add_argument("-i", "--incomplete", dest="show", action="store_const", const="INCOMPLETE", default="NO", help = "show only incomplete lessons")
    argument_parser.add_argument("-b", "--db", dest="db", action="store", type=str, default=DEFAULT_DB, help="database url (%s by defaul)" % DEFAULT_DB)
    argument_parser.add_argument("--debug", dest = "debug", action="store_true", help="set debug mode")
    argument_parser.add_argument("-f", "--force", dest="force", action="store_true", help="put data into database without dialog message")


    args = argument_parser.parse_args()
    SHOW: str = args.show
    db_url: str = args.db
    filedir: str = args.dir
    DEBUG: bool = args.debug
    #sheets = parse_table("./table.xls")

    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)

    lessons: Dict[str, List[Optional[Lesson]]] = {}
    FILES: List[str] = []

    for file in os.listdir(filedir):
        ext = file.split(".")[-1]
        if ext == "xls":
            logging.debug(f"added {file}")
            FILES.append(os.path.join(filedir, file))
        else:
            logging.debug(f"skiped {file}")

    if PROGRESS:
        FILES = tqdm(FILES, position=0, leave=True, desc="files")

    for table in FILES:
        logging.debug("parsing file: " + table)
        sheets = parse_table(table)
        for sheet_name, sheet in sheets.items():
            logging.debug("   SHEET: " + sheet_name)
            l = parse_sheet(sheet)
            lessons.update(l)

    print(f"Total: {TOTAL}")
    print(f"{colorama.Fore.YELLOW}Incomplete: {INCOMPLETE}{colorama.Fore.RESET}")
    print(f"{colorama.Fore.GREEN}Passed: {PASSED}{colorama.Fore.RESET}")
    print(f"{colorama.Fore.RED}Unnamed: {UNNAMED}{colorama.Fore.RESET}")
    print(f"{colorama.Fore.RED}Errors: {ERRORS}{colorama.Fore.RESET}")

    is_updating: str = input("Put data into database (%s)? [y/n]: " % db_url)
    if is_updating.lower() == "y":
        upd = Updater(db_url)
        upd.clear_schedule()
        print("Adding lessons list: ", end = "")
        upd.add_lessons(LESSONS_SET)
        print("OK")
        print("Adding authors list: ", end = "")
        upd.add_authors(AUTHORS_SET)
        print("OK")

        if PROGRESS:
            lessons_list = tqdm(lessons.items())
        else:
            lessons_list = lessons.items()

        for group, sch in lessons_list:
            upd.add_group(group, sch)
    else:
        print("Abort")
    