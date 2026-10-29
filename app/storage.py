"""Versioned document repository. MongoDB in production; SQLite for demo/tests."""
import json
import sqlite3
from pathlib import Path
from threading import RLock

class Conflict(Exception):
    pass

class SQLiteStore:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.lock = RLock()
        self.conn.execute('CREATE TABLE IF NOT EXISTS records (tenant TEXT, kind TEXT, id TEXT, version INTEGER, data TEXT, PRIMARY KEY(tenant,kind,id))')
        self.conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS employee_username ON records (tenant, json_extract(data, '$.username')) WHERE kind='employees' AND json_extract(data, '$.username') IS NOT NULL")
        self.conn.commit()
    def list(self, tenant, kind):
        with self.lock:
            column="json_remove(data, '$.content')" if kind=='documents' else 'data'
            rows = self.conn.execute(f'SELECT {column} FROM records WHERE tenant=? AND kind=?', (tenant, kind)).fetchall()
        return [json.loads(r[0]) for r in rows]
    def get(self, tenant, kind, id):
        with self.lock:
            row = self.conn.execute('SELECT data FROM records WHERE tenant=? AND kind=? AND id=?', (tenant, kind, id)).fetchone()
        return json.loads(row[0]) if row else None
    def create(self, tenant, kind, record):
        record = {**record, 'version': 1}
        with self.lock:
            try:
                self.conn.execute('INSERT INTO records VALUES (?,?,?,?,?)', (tenant,kind,record['id'],1,json.dumps(record)))
                self.conn.commit()
            except sqlite3.IntegrityError:
                raise Conflict('Záznam již existuje.')
        return record
    def update(self, tenant, kind, record, version):
        record = {**record, 'version': version + 1}
        with self.lock:
            try:
                cur = self.conn.execute('UPDATE records SET version=?,data=? WHERE tenant=? AND kind=? AND id=? AND version=?', (version+1,json.dumps(record),tenant,kind,record['id'],version))
                self.conn.commit()
            except sqlite3.IntegrityError:
                self.conn.rollback()
                raise Conflict('Uživatelské jméno již existuje.')
        if not cur.rowcount:
            raise Conflict('Záznam mezitím upravil jiný uživatel. Obnovte stránku.')
        return record

class MongoStore:
    def __init__(self, uri, database):
        from pymongo import MongoClient
        self.client = MongoClient(uri, serverSelectionTimeoutMS=8000)
        self.client.admin.command('ping')
        self.records = self.client[database].records
        self.records.create_index([('tenant',1),('kind',1),('id',1)], unique=True)
        self.records.create_index([('tenant',1),('data.username',1)], unique=True,
            partialFilterExpression={'kind':'employees','data.username':{'$type':'string'}})
    def list(self, tenant, kind):
        projection={'data.content':0} if kind=='documents' else {'data':1}
        return [r['data'] for r in self.records.find({'tenant':tenant,'kind':kind}, projection)]
    def get(self, tenant, kind, id):
        r = self.records.find_one({'tenant':tenant,'kind':kind,'id':id})
        return r['data'] if r else None
    def create(self, tenant, kind, record):
        from pymongo.errors import DuplicateKeyError
        record = {**record, 'version':1}
        try:
            self.records.insert_one({'tenant':tenant,'kind':kind,'id':record['id'],'version':1,'data':record})
        except DuplicateKeyError:
            raise Conflict('Záznam již existuje.')
        return record
    def update(self, tenant, kind, record, version):
        from pymongo.errors import DuplicateKeyError
        record = {**record,'version':version+1}
        try:
            result = self.records.update_one({'tenant':tenant,'kind':kind,'id':record['id'],'version':version}, {'$set':{'version':version+1,'data':record}})
        except DuplicateKeyError:
            raise Conflict('Uživatelské jméno již existuje.')
        if not result.modified_count:
            raise Conflict('Záznam mezitím upravil jiný uživatel. Obnovte stránku.')
        return record
