import argparse

from .run import FUNCTION, MODULE, run
from .usage import usage


def main(args):
    kwargs = vars(args)
    cmd = kwargs.pop('subcommand')
    if cmd is None:
        cmd = 'usage'
    globals()[cmd](**kwargs)

if __name__ == '__main__':
    cli = argparse.ArgumentParser(description='Reactors SDK CLI')
    subparsers = cli.add_subparsers(dest='subcommand')

    # run [file.py] [function] [args]
    parser_a = subparsers.add_parser('run')
    parser_a.add_argument('module', nargs='?', default=MODULE, help='Python module or script')
    parser_a.add_argument('function', nargs='?', default=FUNCTION, help='Name of main function')
    # parser_a.add_argument('args', nargs='*', default=FUNCTION, help='Arguments to pass to function')

    # usage
    parser_b = subparsers.add_parser('usage')
    main(cli.parse_args())

