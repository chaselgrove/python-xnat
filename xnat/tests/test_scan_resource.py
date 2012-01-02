import pyxnat.core.resources
from .. import Connection, _File, _Dictionary

def setup():
    global connection, project, subject, experiment, scan, resource
    connection = Connection('https://central.xnat.org', 
                            'nosetests', 
                            'nosetests')
    project = connection.projects['PALS']
    subject = project.subjects['Human_Buckner_Case01']
    experiment = subject.experiments['Human_Buckner_Case01']
    scan = experiment.scans['mpr-1']
    resource = scan.resources['ANALYZE']

def test_attributes():
    assert resource.connection is connection
    assert resource.project is project
    assert resource.subject is subject
    assert resource.experiment is experiment
    assert resource.scan is scan
    assert isinstance(resource.pyxnat_resource, pyxnat.core.resources.Resource)
    assert resource.id == 1408
    assert resource.label == 'ANALYZE'

def test_files():
    assert isinstance(resource.files, _Dictionary)
    assert 'OAS1_0054_MR1_mpr-1_anon.img' in resource.files
    assert isinstance(resource.files['OAS1_0054_MR1_mpr-1_anon.img'], _File)
    assert 'xxxxxxxx' not in resource.files
    assert len(resource.files) == 3

def teardown():
    connection.close()

# eof
