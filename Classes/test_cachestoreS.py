import pytest
import cachestoreS
import threading

def test_init():
    columns = [["COUNT","INT"],["NOMBRE","TEXT"]]
    c = cachestoreS.CacheStoreSqlite("temp.db", columns)

def test_set():
    columns = [["COUNT","INT"],["NOMBRE","TEXT"]]
    c = cachestoreS.CacheStoreSqlite("temp.db", columns)
    set_val = ["10","11","\'Acc\'"]
    c.set(set_val)

def test_get():
    columns = [["COUNT","INT"],["NOMBRE","TEXT"]]
    c = cachestoreS.CacheStoreSqlite("temp.db", columns)
    t = c.get("10")

def test_set_get():
    columns = [["COUNT","INT"],["NOMBRE","TEXT"]]
    c = cachestoreS.CacheStoreSqlite("temp.db", columns)
    set_val = ["10","11","\'Acc\'"]
    c.set(set_val)
    t = c.get("10")
    assert [(10,11,'Acc')] == t
