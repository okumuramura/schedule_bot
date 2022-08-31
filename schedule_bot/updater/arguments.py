import argparse

from schedule_bot import DB_URL


argument_parser = argparse.ArgumentParser()
argument_parser.add_argument(
    "-d",
    "--dir",
    dest="dir",
    action="store",
    type=str,
    default="./",
    help="directory with files",
)
argument_parser.add_argument(
    "-a",
    "--all",
    dest="show",
    action="store_const",
    const="ALL",
    default="NO",
    help="show all lessons",
)
argument_parser.add_argument(
    "-i",
    "--incomplete",
    dest="show",
    action="store_const",
    const="INCOMPLETE",
    default="NO",
    help="show only incomplete lessons",
)
argument_parser.add_argument(
    "-b",
    "--db",
    dest="db",
    action="store",
    type=str,
    default=DB_URL,
    help="database url (%s by defaul)" % DB_URL,
)
argument_parser.add_argument(
    "--debug", dest="debug", action="store_true", help="set debug mode"
)
argument_parser.add_argument(
    "-f",
    "--force",
    dest="force",
    action="store_true",
    help="put data into database without dialog message",
)
