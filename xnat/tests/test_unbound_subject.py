import nose.tools
import pyxnat.core.resources
from .. import Connection, _UnboundExperiment

def setup():
    global c, s
    c = Connection('https://central.xnat.org/', 'nosetests', 'nosetests')
    s = c.get_subject('OAS1_0001')

def test_nonexistent():
    nose.tools.assert_raises(ValueError, lambda: c.get_subject('xxxxxxxx'))

def test_attributes():
    assert s.connection is c
    assert s.id == 'OAS1_0001'
    nose.tools.assert_raises(AttributeError, lambda: s.label)
    nose.tools.assert_raises(AttributeError, lambda: s.project)
    assert isinstance(s.pyxnat_subject, pyxnat.core.resources.Subject)
    assert s.primary_label == 'OAS1_0001'
    assert s.primary_project is c.projects['CENTRAL_OASIS_CS']
    assert isinstance(s.xml, str)
    s.xml.startswith('<xnat:Subject ID="CENTRAL_S00088"')
    s.xml.endswith('</xnat:Subject>\n')

def test_projects():
    assert isinstance(s.projects, list)
    assert len(s.projects) == 1
    assert c.projects['CENTRAL_OASIS_CS'] in s.projects

def test_experiments():
    assert isinstance(s.experiments, dict)
    assert len(s.experiments) == 1
    assert 'OAS1_0001_CLIN_1' in s.experiments
    assert isinstance(s.experiments['OAS1_0001_CLIN_1'], _UnboundExperiment)

def teardown():
    c.close()

# eof
