import pyxnat.core.resources
from .. import Connection

def setup():
    global c, s
    c = Connection('https://central.xnat.org/', 'nosetests', 'nosetests')
    s = c.projects['PALS'].subjects['Human_Buckner_Case01']

def test_attributes():
    assert s.connection is c
    assert s.id == 'OAS1_0054'
    assert isinstance(s.pyxnat_subject, pyxnat.core.resources.Subject)
    assert s.primary_label == 'OAS1_0054'
    assert s.primary_project is c.projects['CENTRAL_OASIS_CS']
    assert isinstance(s.xml, str)
    s.xml.startswith('<xnat:Subject ID="OAS1_0054"')
    s.xml.endswith('</xnat:Subject>\n')

def test_bound_attributes():
    assert s.project is c.projects['PALS']
    assert s.label == 'Human_Buckner_Case01'

def test_projects():
    assert isinstance(s.projects, list)
    assert len(s.projects) == 2
    assert c.projects['PALS'] in s.projects
    assert c.projects['CENTRAL_OASIS_CS'] in s.projects

def teardown():
    c.close()

# eof
