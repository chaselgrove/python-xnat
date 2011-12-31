#def test_repr():
#def test_str():

import nose.tools
from .. import Dictionary

t = ((1, 'z'), 
     (5, 'v'), 
     (3, 'x'), 
     (4, 'w'), 
     (2, 'y'))

def setitem(key):
    d[key] = None

def delitem(key):
    del d[key]

def setup():
    global d
    d = Dictionary(t)

def test_contains():
    assert 1 in d
    assert 6 not in d

def test_delitem():
    nose.tools.assert_raises(AttributeError, lambda: delitem(1))
    nose.tools.assert_raises(AttributeError, lambda: delitem(6))

def test_iter():
    assert [ k for k in d ] == [1, 5, 3, 4, 2]

def test_len():
    assert len(d) == 5

def test_setitem():
    nose.tools.assert_raises(AttributeError, lambda: setitem(1))
    nose.tools.assert_raises(AttributeError, lambda: setitem(6))

def test_has_key():
    assert 1 in d
    assert 6 not in d

def test_items():
    assert d.items() == list(t)

def test_iteritems():
    assert [ v for v in d.iteritems() ] == list(t)

def test_iterkeys():
    assert [ k for k in d.iterkeys() ] == [1, 5, 3, 4, 2]

def test_itervalues():
    assert [ v for v in d.itervalues() ] == ['z', 'v', 'x', 'w', 'y']

def test_keys():
    assert d.keys() == [1, 5, 3, 4, 2]

def test_values():
    assert d.values() == ['z', 'v', 'x', 'w', 'y']

# eof
