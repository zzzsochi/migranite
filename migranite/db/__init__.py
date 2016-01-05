from .json import JSON
from .mongo import Mongo


def get(config):
    """ Get database object
    """
    if config['database']['backend'] == 'json':
        return JSON(config)
    elif config['database']['backend'] == 'mongo':
        return Mongo(config)
    else:
        raise RuntimeError("Bad database backend: {}".format(config['database']))
