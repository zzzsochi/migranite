import argparse
import configparser
import os
import sys

from migranite import __version__
import migranite.run
import migranite.utils


def _require_config(func):
    def wrapper(parser, args):
        if 'migrations' in args.config:
            func(parser, args)
        else:
            print("Config file {!r} not found".format(args.config['file']),
                  file=sys.stderr)
            sys.exit(1)

    return wrapper


def run_init(parser, args):
    config_path = args.config['file']

    if os.path.exists(config_path):
        print("Config file {!r} is already exists".format(config_path),
              file=sys.stderr)
        sys.exit(1)

    migranite.run.init(args.config, args.migrations, args.templates)


@_require_config
def run_list(parser, args):
    migranite.run.print_list(args.config, args.long)


@_require_config
def run_create(parser, args):
    if not args.template:
        if 'default' not in args.config['templates']:
            print("Default template not set.", file=sys.stderr)
            sys.exit(1)

        template = args.config['templates']['default']

    template = os.path.join(args.config['templates']['path'], template)

    if not os.path.isfile(template):
        print("{!r} is not exist".format(template), file=sys.stderr)
        sys.exit(1)

    migranite.run.create(args.config, template, args.name[0])


@_require_config
def run(parser, args):
    if args.migrations:
        migranite.run.migrate(
            args.config, args.migrations, args.force)
    else:
        migranite.run.migrate_all(args.config)


def run_help(parser, args):
    parser.print_help()


def run_version(parser, args):
    print(__version__)


def _parse_config(path):
    path = migranite.utils.parse_path(path)

    try:
        with open(path, 'r', encoding='utf8') as f:
            raw = f.read()
    except FileNotFoundError:
        return {'file': path}

    config_reader = configparser.ConfigParser()
    config_reader.read_string(raw)

    for section in ['migrations', 'templates', 'database']:
        if section not in config_reader:
            print("Config has no {!r} section".format(section), file=sys.stderr)
            sys.exit(1)

    config = {
        'file': path,
        'migrations': dict(config_reader.items('migrations')),
        'templates': dict(config_reader.items('templates')),
        'database': dict(config_reader.items('database')),
    }

    config['migrations']['path'] = migranite.utils.parse_path(config['migrations']['path'])
    config['migrations']['digits'] = int(config['migrations'].get('digits', 3))
    config['templates']['path'] = migranite.utils.parse_path(config['templates']['path'])

    return config


def main():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('--config',
                        type=_parse_config,
                        default='.migranite',
                        help="config file (default '.migranite')")

    subparsers = parser.add_subparsers()

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

    parser_list = subparsers.add_parser('list', help="show all available migrations")
    parser_list.set_defaults(func=run_list)

    parser_list.add_argument('-l', '--long',
                             action='store_true',
                             help="show long descriprions")

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

    parser_run = subparsers.add_parser('run', help="run migrations")
    parser_run.set_defaults(func=run)

    parser_run.add_argument('migrations',
                            nargs='*',
                            help="migrations for run")

    parser_run.add_argument('-f', '--force',
                            action='store_true',
                            help="force run specified migrations")

    parser_help = subparsers.add_parser('help', help="show this help message and exit")
    parser_help.set_defaults(func=run_help)

    parser_version = subparsers.add_parser('version', help="show version and exit")
    parser_version.set_defaults(func=run_version)

    args = parser.parse_args()
    getattr(args, 'func', run_help)(parser, args)


if __name__ == '__main__':
    main()
