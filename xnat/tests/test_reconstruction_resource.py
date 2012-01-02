import pyxnat.core.resources
from .. import Connection, _File, _Dictionary

def setup():
    global connection, project, subject, experiment, reconstruction, in_resource, out_resource
    connection = Connection('https://central.xnat.org', 
                            'nosetests', 
                            'nosetests')
    project = connection.projects['nosetests']
    subject = project.subjects['resource_test']
    experiment = subject.experiments['resource_test_MR']
    reconstruction = experiment.reconstructions['recon']
    in_resource = reconstruction.in_resources['tir']
    out_resource = reconstruction.out_resources['tor']

def test_attributes():
    assert in_resource.connection is connection
    assert out_resource.connection is connection
    assert in_resource.project is project
    assert out_resource.project is project
    assert in_resource.subject is subject
    assert out_resource.subject is subject
    assert in_resource.experiment is experiment
    assert out_resource.experiment is experiment
    assert in_resource.reconstruction is reconstruction
    assert out_resource.reconstruction is reconstruction
    assert isinstance(in_resource.pyxnat_resource, pyxnat.core.resources.Resource)
    assert isinstance(out_resource.pyxnat_resource, pyxnat.core.resources.Resource)
    assert in_resource.id == 123221303
    assert out_resource.id == 123221304
    assert in_resource.label == 'tir'
    assert out_resource.label == 'tor'

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
