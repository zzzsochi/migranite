import abc
import os
import hashlib


class MigrationInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, settings, file_name, verbose=False):
        pass

    @abc.abstractproperty
    def settings(self):
        """ Settings dict.
        """

    @abc.abstractproperty
    def file_name(self):
        """ Migration file name.
        """

    @abc.abstractproperty
    def verbose(self):
        """ Verbose flag.
        """

    @abc.abstractproperty
    def num(self):
        """ Number representation of migration.
        """

    @abc.abstractproperty
    def name(self):
        """ Name of migration.
        """

    @abc.abstractproperty
    def source(self):
        """ Migration source code.
        """

    @abc.abstractproperty
    def md5(self):
        """ Migration source code md5.
        """

    @abc.abstractproperty
    def short(self):
        """ One-line description.
        """

    @abc.abstractproperty
    def long(self):
        """ Multiline long description.
        """

    @abc.abstractmethod
    def run(self):
        """ Migration logic.
        """

    @abc.abstractmethod
    def __lt__(self, other):
        pass

    @abc.abstractmethod
    def __eq__(self, other):
        pass


class MigrationBase(MigrationInterface):
    _source = None

    def __init__(self, settings, file_name, verbose=False):
        self._settings = settings
        self._file_name = file_name
        self._verbose = verbose

        file_base_name = os.path.splitext(file_name)[0]
        num, name = file_base_name.split('-', 1)
        self._num = int(num)
        self._name = name

    @property
    def settings(self):
        return self._settings

    @property
    def file_name(self):
        return self._file_name

    @property
    def verbose(self):
        return self._verbose

    @property
    def num(self):
        return self._num

    @property
    def name(self):
        return self._name

    @property
    def source(self):
        if self._source is None:
            f = open(os.path.join(self.settings['migrations']['path'], self.file_name), 'r')
            with f:
                self._source = f.read()
        return self._source

    @property
    def md5(self):
        return hashlib.md5(self.source.encode('utf8')).hexdigest()

    def __lt__(self, other):
        if self.num == other.num:
            return self.name < other.name
        else:
            return self.num < other.num

    def __eq__(self, other):
        return self.num == other.num and self.name == other.name

    def __repr__(self):
        return "<{} {!s}>".format(self.__class__.__name__, self.file_name)

    def __str__(self):
        return "{m.num}-{m.name}: {m.short}".format(m=self)
