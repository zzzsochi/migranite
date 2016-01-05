import sys

import json
from datetime import datetime

import dateutil.parser

from .base import DBSimpleBase, MigrationResult


class JSON(DBSimpleBase):
    _results = None

    def __init__(self, config):
        super().__init__(config)
        if 'path' not in config['database']:
            print("Path to json file not set in settings.", file=sys.stderr)
            sys.exit(1)

        self.path = config['database']['path']

    @property
    def results(self):
        if self._results is None:
            try:
                with open(self.path, 'r', encoding='utf8') as f:
                    raw = json.load(f)
            except FileNotFoundError:
                raw = []
            except json.decoder.JSONDecodeError:
                raise RuntimeError("Bad {} format".format(self.path))

            results = []

            for raw_obj in raw:
                result = self._result_from_json(raw_obj)
                results.append(result)

            self._results = results

        return self._results

    def add(self, migration, result):
        r = self._result_from_migration(migration, result)
        self.results.append(r)
        self._save_results()

    @staticmethod
    def _result_from_migration(migration, result):
        return MigrationResult(
            ts=datetime.now(),
            num=migration.num,
            name=migration.name,
            source=migration.source,
            md5=migration.md5,
            result=result,
        )

    @staticmethod
    def _result_from_json(raw):
        return MigrationResult(
            ts=dateutil.parser.parse(raw['ts']),
            num=int(raw['num']),
            name=raw['name'],
            source=raw['source'],
            md5=raw['md5'],
            result=raw['result'],
        )

    @staticmethod
    def _result_to_json(result):
        return {
            'ts': result.ts.isoformat(sep='T'),
            'num': result.num,
            'name': result.name,
            'source': result.source,
            'md5': result.md5,
            'result': result.result,
        }

    def _save_results(self):
        raw = [self._result_to_json(r) for r in self.results]
        with open(self.path, 'w', encoding='utf8') as f:
            json.dump(raw, f, indent=2)
