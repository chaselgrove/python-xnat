import dateutil.parser
import pyxnat.core.resources
from .. import Connection

def setup():
    global connection, project, subject, experiment, scan, resource, file
    connection = Connection('https://central.xnat.org', 
                            'nosetests', 
                            'nosetests')
    project = connection.projects['PALS']
    subject = project.subjects['Human_Buckner_Case01']
    experiment = subject.experiments['Human_Buckner_Case01']
    scan = experiment.scans['mpr-1']
    resource = scan.resources['ANALYZE']
    file = resource.files['OAS1_0054_MR1_mpr-1_anon.hdr']

def test_attributes():
    assert file.connection is connection
    assert file.resource is resource
    assert isinstance(file.pyxnat_file, pyxnat.core.resources.File)
    assert file.path == 'OAS1_0054_MR1_mpr-1_anon.hdr'
    assert file.size == 348
    assert file.last_modified == dateutil.parser.parse('Thu, 13 Jul 2006 14:20:07 GMT')

def test_data():
    data = file.read()
    assert isinstance(data, str)
    assert len(data) == 348

def teardown():
    connection.close()

# eof
