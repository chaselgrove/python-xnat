import pyxnat.core.resources
from .. import Connection, _File, _Dictionary

def setup():
    global connection, project, resource
    connection = Connection('https://central.xnat.org', 
                            'nosetests', 
                            'nosetests')
    project = connection.projects['nosetests']
    resource = project.resources['hx']

def test_attributes():
    assert resource.connection is connection
    assert resource.project is project
    assert isinstance(resource.pyxnat_resource, pyxnat.core.resources.Resource)
    assert resource.id == 123221286
    assert resource.label == 'hx'

def test_files():
    assert isinstance(resource.files, _Dictionary)
    assert 'hello' in resource.files
    assert isinstance(resource.files['hello'], _File)
    assert 'xxxxxxxx' not in resource.files
    assert len(resource.files) == 1

def teardown():
    connection.close()

# eof
