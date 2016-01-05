import types

from .base import MigrationBase


class MigrationPy(MigrationBase):
    _source = None
    _module = None
    _short = None
    _long = None

    @property
    def short(self):
        if self._short is None:
            self._read_doc()
        return self._short

    @property
    def long(self):
        if self._long is None:
            self._read_doc()
        return self._long

    def run(self):
        self.module.run()

    @property
    def module(self):
        if self._module is None:
            self._read_module()
        return self._module

    def _read_module(self):
        self._module = types.ModuleType(self.file_name)
        exec(self.source, self.module.__dict__)

    def _read_doc(self):
        raw = self.module.__doc__.strip()
        if '\n' in raw:
            t = tuple(s.strip() for s in raw.split('\n', 1))
            self._short, self._long = t
        else:
            self._short, self._long = raw, ''
