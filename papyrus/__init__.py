import argparse

from ._version import __version__
from .config import *
from .init import init
from .clean import clean
from .build import build
from .serve import serve
from .deploy import deploy


def main():
    conf = read_config()

    parser = argparse.ArgumentParser(description='A simple static site generator.')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    subparsers = parser.add_subparsers()

    parser_init = subparsers.add_parser('init')
    parser_init.set_defaults(func=init)

    parser_clean = subparsers.add_parser('clean')
    parser_clean.set_defaults(func=clean)

    parser_build = subparsers.add_parser('build')
    parser_build.add_argument('--target', default='dev', choices=['dev', 'prod'])
    parser_build.set_defaults(func=build)

    parser_serve = subparsers.add_parser('serve')
    parser_serve.set_defaults(func=serve)

    # TODO:
    #parser_deploy = subparsers.add_parser('deploy')
    #parser_deploy.add_argument('--dry-run', action='store_true')
    #parser_deploy.set_defaults(func=deploy)

    args = parser.parse_args()
    args.func(args, conf)

