import nose.tools
import pyxnat.core.resources
from .. import Connection

def set_s2_connection():
    s2.connection = ''

def set_s2_project():
    s2.project = ''

def set_s2_subject():
    s2.subject = ''

def set_s2_experiment():
    s2.experiment = ''

def set_s2_id():
    s2.id = ''

def set_s2_pyxnat_scan():
    s2.pyxnat_scan = ''

def set_s2_xml():
    s2.xml = ''

def set_s2_resources():
    s2.resources = ''

def setup():
    global connection, project, subject, experiment, scan
    global s2
    connection = Connection('https://central.xnat.org', 
                            'nosetests', 
                            'nosetests')
    project = connection.projects['PALS']
    subject = project.subjects['Human_Buckner_Case01']
    experiment = subject.experiments['Human_Buckner_Case01']
    scan = experiment.scans['mpr-1']
    raise NotImplementedError, 'need s2 and delete'
    s2 = None

def test_attributes():
    assert scan.connection is connection
    assert scan.project is project
    assert scan.subject is subject
    assert scan.experiment is experiment
    assert scan.id == 'mpr-1'
    assert isinstance(scan.pyxnat_scan, pyxnat.core.resources.Scan)
    assert isinstance(scan.xml, str)
    assert scan.xml.startswith('<?xml version="1.0" encoding="UTF-8"?>\n<xnat:MRScan ID="mpr-1"')
    assert scan.xml.endswith('</xnat:MRScan>\n')

def test_read_only():
    assert nose.tests.assert_raises(AtributeError, set_s2_connection)
    assert nose.tests.assert_raises(AtributeError, set_s2_project)
    assert nose.tests.assert_raises(AtributeError, set_s2_subject)
    assert nose.tests.assert_raises(AtributeError, set_s2_experiment)
    assert nose.tests.assert_raises(AtributeError, set_s2_id)
    assert nose.tests.assert_raises(AtributeError, set_s2_pyxnat_scan)
    assert nose.tests.assert_raises(AtributeError, set_s2_xml)
    assert nose.tests.assert_raises(AtributeError, set_s2_resources)

def teardown():
    connection.close()

# eof
