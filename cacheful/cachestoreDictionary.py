"""
Module for cache connection handling and setup of a dictionary
requirements numpy
"""
import os
import pickle

class CacheStoreDictionary(dict):
    """
    Class that manages the sqlite cache
    """

    def __init__(self, origin):
    	if self._validate_origin(origin):
            self.origin = origin
        else:
            raise TypeError("Just name, without extension")
        self.store = {}
        self._load()

    def get(self, ID):
        row = []
        row.append(ID)
        row.append(self.store[ID])
        return row

    def set(self, set_values):
        self.store[set_values[0]] = set_values[1:]
        self.commit()

    def commit(self):
        if self._dbexists():
            with open(self.origin, 'wb') as f:
                pickle.dump(self.store, f)
        else:
            raise IOError("Database file doesn't exist")

    def _load(self):
        if self._dbexists():
            try:
                with open(self.origin, 'rb') as f:
                    self.store = pickle.load(f)
            except EOFError:
                pass
        else:
            self._createdb()

    def _dbexists(self):
        return os.path.isfile(self.origin)

    def _createdb(self):
        f = open(self.origin, 'wb')
        f.close()

    def _validate_origin(self, origin):
        if isinstance(origin, str):
            for letter in origin:
                if letter == '.':
                    return False
                else:
                    pass
            return True
        else:
            return False
