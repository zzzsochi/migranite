import os
import sys

from colorama import Fore, Style

from . import migrations
from .db import get as get_db


def init(settings, migrations, templates):
    from . import init_data

    settings_path = settings['file']
    settings_dir = os.path.dirname(settings_path)
    os.makedirs(settings_dir, exist_ok=True)

    with open(settings_path, 'w') as f:
        data = init_data.SETTINGS.safe_substitute(
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


def print_list(settings, long=False, all=False):
    """ Print list of available migrations.

    :settings: settings dict
    """
    db = get_db(settings)

    def print_item(item, status, long=False):
        if status == 'PSS':
            color = Fore.GREEN
        elif status == 'ERR':
            color = Fore.RED
        else:
            color = ''

        print("[{C}{status}{R}] {item.num}-{item.name}: {item.short}".format(
            status=status, item=item, C=color, R=Style.RESET_ALL))

        if long and item.long:
            print("\n{}\n".format(item.long))

    if all:
        for result in db.results:
            print_item(result, 'PSS' if result.result else 'ERR', long=long)

    for item in migrations.get_files(settings):
        item = migrations.get(settings, item)

        if db.success(item):
            status = 'PSS'
        elif db.find(item):
            status = 'ERR'
        else:
            status = '   '

        if all and status.strip():
            continue

        print_item(item, status, long=long)


def create(settings, template, name):
    """ Create new migration.

    :temlate: template name
    :name: migration name
    """
    with open(template) as f:
        data = f.read()

    digits = settings.get('digits', 3)
    _, ext = os.path.splitext(template)

    num = max([m.num for m in migrations.get_all(settings)] + [0]) + 1

    name = '{}-{}{}'.format(str(num).zfill(digits), name, ext)

    path = os.path.join(settings['migrations']['path'], name)

    with open(path, 'w') as f:
        f.write(data)


def migrate(settings, migrations_names, force=False):
    """ Run specified migrations.

    :settings: settings dict
    :migrations_names: list of migrations names
    :force: run if migration already worked (default False)
    """
    db = get_db(settings)
    objects = migrations.get_all(settings)
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


def migrate_all(settings):
    """ Run all migrations.

    :settings: settings dict
    """
    db = get_db(settings)
    for migration in migrations.get_all(settings):
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
