import os
import sys

from colorama import Fore, Style

from . import migrations
from .db import get as get_db


def init(config, migrations, templates):
    from . import init_data

    config_path = config['file']
    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)

    with open(config_path, 'w') as f:
        data = init_data.CONFIG.safe_substitute(
            migranite_path=migrations,
            templates_path=templates,
        )
        f.write(data)

    os.makedirs(migrations, exist_ok=True)
    os.makedirs(templates, exist_ok=True)

    templates_default_path = os.path.join(templates, 'default.py')
    if not os.path.exists(templates_default_path):
        with open(templates_default_path, 'w') as f:
            f.write(init_data.TEMPLATE_DEFAULT)
    else:
        print("{!r} is already exist. Skip.".format(templates_default_path),
              file=sys.stderr)


def print_list(config, long=False):
    """ Print list of available migrations

    :config: config dict
    """
    db = get_db(config)

    for migration in migrations.get_files(config):
        migration = migrations.get(config, migration)

        if db.success(migration):
            status = 'PSS'
            color = Fore.GREEN
        elif db.find(migration):
            status = 'ERR'
            color = Fore.RED
        else:
            status = '   '
            color = ''

        print("[{S}{}{R}] {!s}".format(
            status, migration, S=color, R=Style.RESET_ALL))

        if long:
            if migration.long:
                print("\n{}\n".format(migration.long))
            else:
                print()


def create(config, template, name):
    """ Create new migration

    :temlate: template name
    :name: migration name
    """
    with open(template) as f:
        data = f.read()

    digits = config.get('digits', 3)
    _, ext = os.path.splitext(template)

    num = max([m.num for m in migrations.get_all(config)] + [0]) + 1

    name = '{}-{}{}'.format(str(num).zfill(digits), name, ext)

    path = os.path.join(config['migrations']['path'], name)

    with open(path, 'w') as f:
        f.write(data)


def migrate(config, migrations_names, force=False):
    """ Run specified migrations

    :config: config dict
    :migrations_names: list of migrations names
    :force: run if migration already worked (default False)
    """
    db = get_db(config)
    objects = migrations.get_all(config)
    found = []

    for mn in migrations_names:
        if '-' in mn and mn.split('-', 1)[0].isdigit():
            num, name = mn.split('-', 1)
            if num.isdigit():
                num = int(num)

        elif mn.isdigit():
            num, name = int(mn), None

        else:
            num, name = None, mn

        found_migrations = migrations.find(objects, num, name)

        if not found_migrations:
            print("Migration {!r} not found".format(mn),
                  file=sys.stderr)
            sys.exit(1)
        elif len(found_migrations) > 1:
            print("More than one migration found for {!r}".format(mn),
                  file=sys.stderr)
            sys.exit(1)
        else:
            migration = found_migrations[0]
            if force or not db.success(migration):
                found.append(migration)
            else:
                print("[{S}SKP{R}] {!s}".format(
                    migration, S=Fore.YELLOW, R=Style.RESET_ALL))

    for migration in sorted(found):
        _run_migration(db, migration)


def migrate_all(config):
    """ Run all migrations

    :config: config dict
    """
    db = get_db(config)
    for migration in migrations.get_all(config):
        if not db.success(migration):
            _run_migration(db, migration)
        else:
            print("[{S}SKP{R}] {!s}".format(
                migration, S=Fore.YELLOW, R=Style.RESET_ALL))


def _run_migration(db, migration):
    print("[{S}RUN{R}] {!s}".format(
        migration, S=Fore.GREEN, R=Style.RESET_ALL))

    try:
        result = False
        migration.run()
        result = True
    finally:
        db.add(migration, result)
        if not result:
            print("[{S}ERR{R}] {!s}".format(
                migration, S=Fore.RED, R=Style.RESET_ALL))
