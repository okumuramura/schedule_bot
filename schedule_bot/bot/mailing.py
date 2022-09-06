import argparse
from typing import NoReturn


class NoExitParser(argparse.ArgumentParser):
    def error(self, error_msg: str) -> NoReturn:
        args = {'prog': self.prog, 'message': error_msg}
        raise Exception(('error: %(message)s\n') % args)


mailing_parser = NoExitParser(add_help=False)
mailing_parser.add_argument('-a', '--all', action='store_true', default=False)
mailing_parser.add_argument(
    '-g',
    '--groups',
    action='store',  # extend?
    dest='groups',
    nargs='+',
    type=str,
)
mailing_parser.add_argument('-m', '--message', action='store', type=str)
