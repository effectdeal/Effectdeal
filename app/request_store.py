"""Request-local memoization. Never shares private records between sessions."""
from copy import deepcopy


class RequestStore:
    def __init__(self, backing):
        self.backing = backing
        self.records = {}
        self.lists = {}

    def get(self, tenant, kind, id):
        key=(tenant,kind,id)
        if key not in self.records:
            self.records[key]=self.backing.get(tenant,kind,id)
        return deepcopy(self.records[key])

    def list(self, tenant, kind, filters=None):
        key=(tenant,kind,tuple(sorted((filters or {}).items())))
        if key not in self.lists:
            self.lists[key]=self.backing.list(tenant,kind,filters)
            if kind!='documents':
                for record in self.lists[key]:
                    self.records[(tenant,kind,record['id'])]=record
        return deepcopy(self.lists[key])

    def create(self, *args):
        result=self.backing.create(*args)
        self.records.clear();self.lists.clear()
        return result

    def update(self, *args):
        result=self.backing.update(*args)
        self.records.clear();self.lists.clear()
        return result
