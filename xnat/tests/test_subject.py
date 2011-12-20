import nose.tools
import pyxnat.core.resources
from .. import Connection, _Subject, _Experiment

def setup():
    global c, p, s
    c = Connection('https://central.xnat.org', 'nosetests', 'nosetests')
    p = c.projects['PALS']
    s = p.subjects['Human_Buckner_Case01']

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
    c.close()

# eof
