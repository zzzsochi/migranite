import sys

from datetime import datetime

try:
    import pymongo
    PYMONGO = True
except ImportError:
    PYMONGO = False

from .base import DBInterface, MigrationResult


class Mongo(DBInterface):
    _collection = None

    def __init__(self, settings):
        if not PYMONGO:
            print("pymongo not installed.", file=sys.stderr)
            sys.exit(1)

        if not settings['database'].get('name'):
            print("Database name not set in settings.", file=sys.stderr)
            sys.exit(1)

        self._settings = settings
        self.host = settings['database'].get('host', 'localhost')
        self.port = int(settings['database'].get('port', 27017))
        self.db_name = settings['database']['name']
        self.collection_name = settings['database'].get('collection', 'migrations')

    @property
    def collection(self):
        if self._collection is None:
            client = pymongo.MongoClient(self.host, self.port)
            db = client[self.db_name]
            self._collection = db[self.collection_name]
            self._collection.create_index([('ts', 1)])
            self._collection.create_index([('num', 1), ('name', 1)])

        return self._collection

    @property
    def results(self):
        docs = self.collection.find().sort([('ts', 1)])
        return [self._result_from_doc(doc) for doc in docs]

    def add(self, migration, result):
        doc = self._doc_from_migration(migration, result)
        self.collection.insert(doc)

    def find(self, migration):
        docs = self.collection.find({
            'num': migration.num,
            'name': migration.name,
        }).sort([('ts', 1)])
        return [self._result_from_doc(doc) for doc in docs]

    def success(self, migration):
        results = self.find(migration)
        return results and results[-1].result

    @staticmethod
    def _doc_from_migration(migration, result):
        return {
            'ts': datetime.now(),
            'num': migration.num,
            'name': migration.name,
            'short': migration.short,
            'long': migration.long,
            'source': migration.source,
            'md5': migration.md5,
            'result': result,
        }

    @staticmethod
    def _result_from_doc(doc):
        return MigrationResult(
            ts=doc['ts'],
            num=doc['num'],
            name=doc['name'],
            short=doc['short'],
            long=doc['long'],
            source=doc['source'],
            md5=doc['md5'],
            result=doc['result'],
        )
