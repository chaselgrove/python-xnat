import pyxnat.core.resources
from .. import Connection

def setup():
    global connection, project, subject, experiment, scan
    connection = Connection('https://central.xnat.org', 
                            'nosetests', 
                            'nosetests')
    project = connection.projects['PALS']
    subject = project.subjects['Human_Buckner_Case01']
    experiment = subject.experiments['Human_Buckner_Case01']
    scan = experiment.scans['mpr-1']

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

def teardown():
    connection.close()

# eof
