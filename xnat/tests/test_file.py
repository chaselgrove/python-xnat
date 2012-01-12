import dateutil.parser
import tempfile
import shutil
import pyxnat.core.resources
from .. import Connection

def setup():
    global connection, project, subject, experiment, scan, resource, file, tempdir
    connection = Connection('https://central.xnat.org', 
                            'nosetests', 
                            'nosetests')
    project = connection.projects['PALS']
    subject = project.subjects['Human_Buckner_Case01']
    experiment = subject.experiments['Human_Buckner_Case01']
    scan = experiment.scans['mpr-1']
    resource = scan.resources['ANALYZE']
    file = resource.files['OAS1_0054_MR1_mpr-1_anon.hdr']
    tempdir = tempfile.mkdtemp()

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
    fname = '%s/temp.hdr' % tempdir
    file.get(fname)
    local_data = open(fname).read()
    assert local_data == data

def teardown():
    connection.close()
    shutil.rmtree(tempdir)

# eof
