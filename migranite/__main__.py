import argparse
import os
import sys

import zini

from migranite import __version__
import migranite.run
import migranite.utils


def _require_settings(func):
    def wrapper(parser, args):
        if 'migrations' in args.settings:
            func(parser, args)
        else:
            print("Settings file {!r} not found".format(args.settings['file']),
                  file=sys.stderr)
            sys.exit(1)

    return wrapper


def run_init(parser, args):
    settings_path = args.settings['file']

    if os.path.exists(settings_path):
        print("Settings file {!r} is already exists".format(settings_path),
              file=sys.stderr)
        sys.exit(1)

    migranite.run.init(args.settings, args.migrations, args.templates)


@_require_settings
def run_list(parser, args):
    migranite.run.print_list(args.settings, args.long, args.all)


@_require_settings
def run_create(parser, args):
    if not args.template:
        if 'default' not in args.settings['templates']:
            print("Default template not set.", file=sys.stderr)
            sys.exit(1)

        template = args.settings['templates']['default']

    template = os.path.join(args.settings['templates']['path'], template)

    if not os.path.isfile(template):
        print("{!r} is not exist".format(template), file=sys.stderr)
        sys.exit(1)

    migranite.run.create(args.settings, template, args.name[0])


@_require_settings
def run(parser, args):
    if args.migrations:
        migranite.run.migrate(
            args.settings, args.migrations, args.force)
    else:
        migranite.run.migrate_all(args.settings)


def run_help(parser, args):
    parser.print_help()


def run_version(parser, args):
    print(__version__)


def _parse_settings(path):
    path = migranite.utils.parse_path(path)

    try:
        with open(path, 'r', encoding='utf8') as f:
            raw = f.read()
    except FileNotFoundError:
        return {'file': path}

    settings_reader = zini.Zini()

    settings_reader['migrations']['path'] = str
    settings_reader['migrations']['digits'] = 3

    settings_reader['templates']['path'] = str
    settings_reader['templates']['default'] = "default.py"

    settings_reader['database']['backend'] = str

    settings = settings_reader.parse(raw)

    err = False

    for section, key in [('migrations', 'path'),
                         ('templates', 'path'),
                         ('database', 'backend')]:
        if key not in settings[section]:
            print(("Section {!r} must include the {!r} key."
                   "".format(section, key)), file=sys.stderr)
            err = True

    if err:
        sys.exit(1)

    return settings


def main():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('--settings',
                        type=_parse_settings,
                        default='.migranite',
                        help="settings file (default '.migranite')")

    subparsers = parser.add_subparsers()

    # init

    parser_init = subparsers.add_parser('init', help="add migranite to project")
    parser_init.set_defaults(func=run_init)

    parser_init.add_argument('--migrations',
                             type=migranite.utils.parse_path,
                             required=True,
                             metavar='DIR',
                             help="migration directory")

    parser_init.add_argument('--templates',
                             type=migranite.utils.parse_path,
                             required=True,
                             metavar='DIR',
                             help="templates directory")

    # list

    parser_list = subparsers.add_parser('list', help="show all available migrations")
    parser_list.set_defaults(func=run_list)

    parser_list.add_argument('-l', '--long',
                             action='store_true',
                             help="show long descriprions")

    parser_list.add_argument('-a', '--all',
                             action='store_true',
                             help="show removed migrations migrations too")

    # create

    parser_create = subparsers.add_parser('create', help="create new migtation")
    parser_create.set_defaults(func=run_create)

    parser_create.add_argument('name',
                               nargs=1,
                               metavar='NAME',
                               help="new migration name")

    parser_create.add_argument('-t', '--template',
                               default=None,
                               metavar='NAME',
                               help="template for new migration")

    # run

    parser_run = subparsers.add_parser('run', help="run migrations")
    parser_run.set_defaults(func=run)

    parser_run.add_argument('migrations',
                            nargs='*',
                            help="migrations for run")

    parser_run.add_argument('-f', '--force',
                            action='store_true',
                            help="force run specified migrations")

    # help

    parser_help = subparsers.add_parser('help', help="show this help message and exit")
    parser_help.set_defaults(func=run_help)

    # version

    parser_version = subparsers.add_parser('version', help="show version and exit")
    parser_version.set_defaults(func=run_version)

    # --

    args = parser.parse_args()
    getattr(args, 'func', run_help)(parser, args)


if __name__ == '__main__':
    main()
