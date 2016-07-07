import pytest
import cachestoreD as ca

def test_init():
	c = ca.cachestoredictionary("test")

def test_set():
	c = ca.cachestoredictionary("test")
	c.set([123,'rfs', 122, 'hola'])

def test_get():
	c = ca.cachestoredictionary("test")
	t = c.get(123)

def test_set_get():
	c = ca.cachestoredictionary("test")
	c.set([124,'rrfs', 5122, 'ghola'])	
	t = c.get(124)
	assert [124,['rrfs', 5122, 'ghola']] == t
