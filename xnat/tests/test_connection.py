import nose.tools
import pyxnat.core.interfaces
from .. import Connection, NotConnectedError, _Project, _Dictionary

def soap_call_http():
    global jsessionid
    inputs = (jsessionid, 
              'wrk:workflowData.ID', 
              '=', 
              'INCF_E00007', 
              'wrk:workflowData')
    return uc._soap_call('GetIdentifiers.jws', 'search', inputs)

def soap_call_https():
    global jsessionid
    inputs = (jsessionid, 
              'wrk:workflowData.ID', 
              '=', 
              'CENTRAL_E00778', 
              'wrk:workflowData')
    return c._soap_call('GetIdentifiers.jws', 'search', inputs)

def setup():
    global c, uc
    c = Connection('https://central.xnat.org/', 'nosetests', 'nosetests')
    uc = Connection('http://xnat.incf.org/xnat', 'nosetests', 'nosetests')

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
    assert isinstance(c.projects, _Dictionary)
    assert 'CENTRAL_OASIS_CS' in c.projects
    assert isinstance(c.projects['CENTRAL_OASIS_CS'], _Project)
    assert 'xxxxxxxx' not in c.projects

def test_private_project():
    assert 'nosetests2' in c.projects

def test_soap():
    global jsessionid
    jsessionid = c._jsessionid
    res = soap_call_https()
    assert isinstance(res, list)
    jsessionid = uc._jsessionid
    res = soap_call_http()
    assert isinstance(res, list)

def test_close():
    c.close()
    assert not c.is_connected()
    uc.close()
    assert not uc.is_connected()

def test_not_connected():
    global jsessionid
    c = Connection('https://central.xnat.org/', 'nosetests', 'nosetests')
    jsessionid = c._jsessionid
    c.close()
    nose.tools.assert_raises(NotConnectedError, c.close)
    nose.tools.assert_raises(NotConnectedError, lambda: c.projects)
    nose.tools.assert_raises(NotConnectedError, soap_call_https)
    uc = Connection('http://xnat.incf.org/xnat', 'nosetests', 'nosetests')
    jsessionid = uc._jsessionid
    uc.close()
    nose.tools.assert_raises(NotConnectedError, soap_call_http)

# eof
