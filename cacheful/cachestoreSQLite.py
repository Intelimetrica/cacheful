"""
Module for cache connection handling and setup of sqlite
"""
import sqlite3
import os

class CacheStoreSqlite(object):
    """
    Class that manages the sqlite cache
    """
    def __init__(self, origin, columns):
        if self._validate_string(origin):
            self.origin = origin
        else:
            raise TypeError("String expected")
        if self._validate_array(columns):
            self.columns = columns
        else:
            raise TypeError("Array expected")
        if self._validate_ID():
            self._createdb()
            self._createtable()
        else:
            raise ValueError("ID column already implemented, see documentation")

    def get(self, ID):
        query = ("Select * From CACHE where ID = "
               + ID
               + ";")
        with self.getconn() as conn:
            cur = conn.cursor()
            cur.execute(query)
            row = cur.fetchall()
            return row

    def set(self, set_values):
        if self._validate_set(self.columns, set_values):
            query = "INSERT INTO CACHE(ID, "
            for col in self.columns:
                query += " " + col[0] + ","
            query = query[:-1] + ") VALUES("
            for val in set_values:
                query += " " + val + ","
            query = query[:-1] + ");"
            with self.getconn() as conn:
                cur = conn.cursor()
                cur.execute(query)
                conn.commit()
        else:
            raise ValueError("Should set the ID value but no the ID column, see documentation")

    def getconn(self):
        """
        This function gives a connection to the variable validating that the DB exists.
        """
        return sqlite3.connect(self.origin)

    def _dbexists(self):
        return os.path.isfile(self.origin)

    def _createdb(self):
        f = open(self.origin, "w")
        f.close()

    def _createtable(self):
        with self.getconn() as conn:
            cur = conn.cursor()
            query = "CREATE TABLE CACHE(ID  INT PRIMARY KEY, "
            for col in self.columns:
                for ele in col:
                    query += " " + ele
                query += " NULL,"
            query = query[:-1] + ");"
            cur.execute(query)
            conn.commit()

    def _validate_string(self,string):
        return isinstance(string, str)

    def _validate_array(self,array):
        if isinstance(array, list):
            return isinstance(array[0], list)

    def _validate_set(self, array_col, array_val):
        if len(array_val) == len(array_col) + 1:
            return True
        else:
            return False

    def _validate_ID(self):
        for col in self.columns:
            for ele in col:
                if ele.upper() == "ID":
                    return False
                else:
                    pass
        return True
