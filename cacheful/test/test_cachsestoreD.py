import pytest
import cacheful.cachestoreDictionary as ca

def test_init():
	c = ca.CacheStoreDictionary("test")

def test_set():
	c = ca.CacheStoreDictionary("test")
	c.set([123,'rfs', 122, 'hola'])

def test_get():
	c = ca.CacheStoreDictionary("test")
	t = c.get(123)

def test_set_get():
	c = ca.CacheStoreDictionary("test")
	c.set([124,'rrfs', 5122, 'ghola'])	
	t = c.get(124)
	assert [124,['rrfs', 5122, 'ghola']] == t
