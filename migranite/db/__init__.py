from .json import JSON
from .mongo import Mongo


def get(settings):
    """ Get database object.
    """
    if settings['database']['backend'] == 'json':
        return JSON(settings)
    elif settings['database']['backend'] == 'mongo':
        return Mongo(settings)
    else:
        raise RuntimeError("Bad database backend: {!r}"
                           "".format(settings['database']))
