import pyxnat.core.resources
from .. import Connection, _File, _Dictionary

def setup():
    global connection, project, subject, experiment, resource
    connection = Connection('https://central.xnat.org', 
                            'nosetests', 
                            'nosetests')
    project = connection.projects['nosetests']
    subject = project.subjects['resource_test']
    experiment = subject.experiments['resource_test_MR']
    resource = experiment.resources['hx']

def test_attributes():
    assert resource.connection is connection
    assert resource.project is project
    assert resource.subject is subject
    assert resource.experiment is experiment
    assert isinstance(resource.pyxnat_resource, pyxnat.core.resources.Resource)
    assert resource.id == 123221300
    assert resource.label == 'hx'

def test_files():
    assert isinstance(resource.files, _Dictionary)
    assert 'h' in resource.files
    assert isinstance(resource.files['h'], _File)
    assert 'xxxxxxxx' not in resource.files
    assert len(resource.files) == 1

def teardown():
    connection.close()

# eof
