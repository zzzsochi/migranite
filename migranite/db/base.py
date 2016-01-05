import abc
from collections import namedtuple


MigrationResult = namedtuple(
    'MigrationResult',
    ('ts', 'num', 'name', 'short', 'long', 'source', 'md5', 'result'))


class DBInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, config):
        pass

    @abc.abstractproperty
    def results(self):
        """ List of all results (MigrationResult)
        """

    @abc.abstractmethod
    def add(self, migration, result):
        """ Add migration result to database
        """

    @abc.abstractmethod
    def find(self, migration):
        """ Fild all results for migration

        Return list of results (MigrationResult).
        """

    @abc.abstractmethod
    def success(self, migration):
        """ Return True if last migration run is success
        """


class DBSimpleBase(DBInterface):
    def __init__(self, config):
        self._config = config

    def find(self, migration):
        return [r for r in self.results
                if r.num == migration.num and r.name == migration.name]

    def success(self, migration):
        results = self.find(migration)

        if not results:
            return False
        else:
            return results[-1].result
