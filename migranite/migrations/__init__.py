import os

from .base import MigrationInterface  # noqa
from .py import MigrationPy


def get_all(settings):
    """ Get all available migtarion.
    """
    return [get(settings, fn) for fn in get_files(settings)]


def get_files(settings):
    path = settings['migrations']['path']
    if not os.path.isdir(path):
        print("{} not exists".format(path))
        return []

    for file_name in sorted(os.listdir(path)):
        if file_name.startswith('.'):
            continue
        elif not os.path.splitext(file_name)[1]:
            continue

        yield file_name


def get(settings, file_name):
    """ Get migration object for file.
    """
    name, ext = os.path.splitext(file_name)

    if ext == '.py':
        return MigrationPy(settings, file_name)
    else:
        raise ValueError("Unknown migration type {!r}".format(file_name))


def find(migrations, num=None, name=None):
    """ Find migtations for num and name.
    """
    result = []

    for migration in migrations:
        if num is not None and name is not None:
            if migration.num == num and migration.name == name:
                result.append(migration)
        elif num is not None:
            if migration.num == num:
                result.append(migration)
        elif name is not None:
            if migration.name == name:
                result.append(migration)
        else:
            result.extend(migrations)

    return result
