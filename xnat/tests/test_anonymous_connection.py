import nose.tools
import pyxnat.core.interfaces
from .. import AnonymousConnection, NotConnectedError, _Project

def setup():
    global c
    c = AnonymousConnection('https://central.xnat.org/')

def test_connection():
    assert c.is_connected()

def test_pyxnat_interface():
    assert isinstance(c.pyxnat_interface, pyxnat.core.interfaces.Interface)

def test_attributes():
    assert c.uri == 'https://central.xnat.org/'
    nose.tools.assert_raises(AttributeError, lambda: c.user)
    nose.tools.assert_raises(AttributeError, lambda: c.password)

def test_projects():
    assert isinstance(c.projects, dict)
    assert 'CENTRAL_OASIS_CS' in c.projects
    assert isinstance(c.projects['CENTRAL_OASIS_CS'], _Project)
    assert 'xxxxxxxx' not in c.projects

def test_private_project():
    assert 'nosetests2' not in c.projects

def test_close():
    c.close()
    assert not c.is_connected()

def test_not_connected():
    c = AnonymousConnection('https://central.xnat.org/')
    c.close()
    nose.tools.assert_raises(NotConnectedError, c.close)
    nose.tools.assert_raises(NotConnectedError, lambda: c.projects)

# eof
