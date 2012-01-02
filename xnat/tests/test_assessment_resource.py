import pyxnat.core.resources
from .. import Connection, _File, _Dictionary

def setup():
    global connection, project, subject, experiment, assessment, in_resource, out_resource
    connection = Connection('https://central.xnat.org', 
                            'nosetests', 
                            'nosetests')
    project = connection.projects['nosetests']
    subject = project.subjects['resource_test']
    experiment = subject.experiments['resource_test_MR']
    assessment = experiment.assessments['assessment']
    in_resource = assessment.in_resources['tia']
    out_resource = assessment.out_resources['toa']

def test_attributes():
    assert in_resource.connection is connection
    assert out_resource.connection is connection
    assert in_resource.project is project
    assert out_resource.project is project
    assert in_resource.subject is subject
    assert out_resource.subject is subject
    assert in_resource.experiment is experiment
    assert out_resource.experiment is experiment
    assert in_resource.assessment is assessment
    assert out_resource.assessment is assessment
    assert isinstance(in_resource.pyxnat_resource, pyxnat.core.resources.Resource)
    assert isinstance(out_resource.pyxnat_resource, pyxnat.core.resources.Resource)
    assert in_resource.id == 123221301
    assert out_resource.id == 123221302
    assert in_resource.label == 'tia'
    assert out_resource.label == 'toa'

def test_files():
    assert isinstance(in_resource.files, _Dictionary)
    assert isinstance(out_resource.files, _Dictionary)
    assert 'hx' in in_resource.files
    assert 'h2' in out_resource.files
    assert isinstance(in_resource.files['hx'], _File)
    assert isinstance(out_resource.files['h2'], _File)
    assert 'xxxxxxxx' not in in_resource.files
    assert 'xxxxxxxx' not in out_resource.files
    assert len(in_resource.files) == 1
    assert len(out_resource.files) == 1

def teardown():
    connection.close()

# eof
