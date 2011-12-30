import uuid
import nose.tools
import pyxnat.core.resources
from .. import Connection, _Subject, _Experiment

def set_s2_connection():
    s2.connection = ''

def set_s2_id():
    s2.id = ''

def set_s2_project():
    s2.project = ''

def set_s2_label():
    s2.label = ''

def set_s2_pyxnat_subject():
    s2.pyxnat_subject = ''

def set_s2_xml():
    s2.xml = ''

def set_s2_primary_project():
    s2.primary_project = ''

def set_s2_primary_label():
    s2.primary_label = ''

def set_s2_projects():
    s2.projects = ''

def set_s2_experiments():
    s2.experiments = ''

def set_s2_experiments_by_id():
    s2.experiments_by_id = ''

def set_s2_resources():
    s2.resources = ''

def setup():
    global c, p, s, s2
    c = Connection('https://central.xnat.org', 'nosetests', 'nosetests')
    p = c.projects['PALS']
    s = p.subjects['Human_Buckner_Case01']
    s2 = c.projects['nosetests'].create_subject(uuid.uuid1().hex)

def test_attributes():
    assert s.connection is c
    assert s.id == 'OAS1_0054'
    assert s.project is p
    assert s.label == 'Human_Buckner_Case01'
    assert isinstance(s.pyxnat_subject, pyxnat.core.resources.Subject)
    assert isinstance(s.xml, str)
    s.xml.startswith('<xnat:Subject ID="OAS1_0054"')
    s.xml.endswith('</xnat:Subject>\n')
    assert s.primary_project is c.projects['CENTRAL_OASIS_CS']
    assert s.primary_label == 'OAS1_0054'

def test_read_only():
    nose.tools.assert_raises(AttributeError, set_s2_connection)
    nose.tools.assert_raises(AttributeError, set_s2_id)
    nose.tools.assert_raises(AttributeError, set_s2_project)
    nose.tools.assert_raises(AttributeError, set_s2_label)
    nose.tools.assert_raises(AttributeError, set_s2_pyxnat_subject)
    nose.tools.assert_raises(AttributeError, set_s2_xml)
    nose.tools.assert_raises(AttributeError, set_s2_primary_project)
    nose.tools.assert_raises(AttributeError, set_s2_primary_label)
    nose.tools.assert_raises(AttributeError, set_s2_projects)
    nose.tools.assert_raises(AttributeError, set_s2_experiments)
    nose.tools.assert_raises(AttributeError, set_s2_experiments_by_id)
    nose.tools.assert_raises(AttributeError, set_s2_resources)

def test_projects():
    assert isinstance(s.projects, list)
    assert len(s.projects) == 2
    assert c.projects['PALS'] in s.projects
    assert c.projects['CENTRAL_OASIS_CS'] in s.projects

def test_experiments():
    assert isinstance(s.experiments, dict)
    # label of an experiment
    assert 'Human_Buckner_Case01' in s.experiments
    # ID of the same experiment
    assert 'OAS1_0054_MR1' not in s.experiments
    assert isinstance(s.experiments['Human_Buckner_Case01'], _Experiment)
    assert isinstance(s.experiments_by_id, dict)
    assert 'OAS1_0054_MR1' in s.experiments_by_id
    assert 'Human_Buckner_Case01' not in s.experiments_by_id
    assert isinstance(s.experiments_by_id['OAS1_0054_MR1'], _Experiment)
    s.experiments_by_id['OAS1_0054_MR1'].id == 'OAS1_0054_MR1'
    s.experiments_by_id['OAS1_0054_MR1'].label == 'Human_Buckner_Case01'

def teardown():
    s2.pyxnat_subject.delete()
    c.close()

# eof
