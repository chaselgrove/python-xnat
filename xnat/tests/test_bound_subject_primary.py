import pyxnat.core.resources
from .. import Connection, _BoundExperiment

def setup():
    global c, s
    c = Connection('https://central.xnat.org/', 'nosetests', 'nosetests')
    s = c.projects['CENTRAL_OASIS_LONG'].subjects['OAS2_0010']

def test_attributes():
    assert s.connection is c
    assert s.id == 'CENTRAL_S00088'
    assert isinstance(s.pyxnat_subject, pyxnat.core.resources.Subject)
    assert s.primary_label == 'OAS2_0010'
    assert s.primary_project is c.projects['CENTRAL_OASIS_LONG']
    assert isinstance(s.xml, str)
    s.xml.startswith('<xnat:Subject ID="OAS1_0054"')
    s.xml.endswith('</xnat:Subject>\n')

def test_bound_attributes():
    assert s.project is c.projects['CENTRAL_OASIS_LONG']
    assert s.label == 'OAS2_0010'

def test_projects():
    assert isinstance(s.projects, list)
    assert len(s.projects) == 1
    assert c.projects['CENTRAL_OASIS_LONG'] in s.projects

def test_experiments():
    assert isinstance(s.experiments, dict)
    assert len(s.experiments) == 2
    assert 'OAS2_0010_MR1' in s.experiments
    assert 'CENTRAL_E00106' not in s.experiments
    assert 'OAS2_0010_MR2' in s.experiments
    assert 'CENTRAL_E00107' not in s.experiments
    assert isinstance(s.experiments['OAS2_0010_MR2'], _BoundExperiment)

def teardown():
    c.close()

# eof
