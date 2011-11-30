import nose.tools
import pyxnat.core.interfaces
from .. import Connection, NotConnectedError, _Project

def setup():
    global c
    c = Connection('https://central.xnat.org/', 'nosetests', 'nosetests')

def test_failed_login():
    nose.tools.assert_raises(pyxnat.core.errors.OperationalError, 
                             lambda: Connection('https://central.xnat.org/', 'nosetests', 'xxxxxxxx'))

def test_connection():
    assert c.is_connected()

def test_pyxnat_interface():
    assert isinstance(c.pyxnat_interface, pyxnat.core.interfaces.Interface)

def test_attributes():
    assert c.uri =='https://central.xnat.org/' 
    assert c.user == 'nosetests'
    nose.tools.assert_raises(AttributeError, lambda: c.password)

def test_projects():
    assert isinstance(c.projects, dict)
    assert 'CENTRAL_OASIS_CS' in c.projects
    assert isinstance(c.projects['CENTRAL_OASIS_CS'], _Project)
    assert 'xxxxxxxx' not in c.projects

def test_private_project():
    assert 'nosetests2' in c.projects

def test_close():
    c.close()
    assert not c.is_connected()

def test_not_connected():
    c = Connection('https://central.xnat.org/', 'nosetests', 'nosetests')
    c.close()
    nose.tools.assert_raises(NotConnectedError, c.close)
    nose.tools.assert_raises(NotConnectedError, lambda: c.projects)

# eof
