import nose.tools
import pyxnat.core.resources
from .. import Connection, _Scan, _Reconstruction, _Assessment, _Workflow, _Dictionary

def set_e2_connection():
    e2.connection = ''

def set_e2_project():
    e2.project = ''

def set_e2_id():
    e2.id = ''

def set_e2_pyxnat_experiment():
    e2.pyxnat_experiment = ''

def set_e2_xml():
    e2.xml = ''

def set_e2_subject():
    e2.subject = ''

def set_e2_label():
    e2.label = ''

def set_e2_primary_subject():
    e2.primary_subject = ''

def set_e2_primary_label():
    e2.primary_label = ''

def set_e2_scans():
    e2.scans = ''

def set_e2_reconstructions():
    e2.reconstructions = ''

def set_e2_assessments():
    e2.assessments = ''

def set_e2_resources():
    e2.resources = ''

def set_e2_workflows():
    e2.workflows = ''

def setup():
    global c, p, s, e, ps, workflow_experiment
    global e2
    c = Connection('https://central.xnat.org', 'nosetests', 'nosetests')
    p = c.projects['PALS']
    s = p.subjects['Human_Buckner_Case01']
    e = s.experiments['Human_Buckner_Case01']
    ps = c.projects['CENTRAL_OASIS_CS'].subjects['OAS1_0054']
    workflow_experiment = c.projects['Calib'].subjects['73213384'].experiments['73213384_DUKE']
#    raise ValueError, 'need e2 set and teardown'
#    e2 = None

def test_attributes():
    assert e.connection is c
    assert e.project is p
    assert e.id == 'OAS1_0054_MR1'
    assert isinstance(e.pyxnat_experiment, pyxnat.core.resources.Experiment)
    assert isinstance(e.xml, str)
    e.xml.startswith('<xnat:MRSession ID="OAS1_0054_MR1"')
    e.xml.endswith('</xnat:MRSession>\n')
    assert e.subject is s
    assert e.label == 'Human_Buckner_Case01'
    assert e.primary_subject is ps
    assert e.primary_label == 'OAS1_0054_MR1'

#def test_read_only():
#    nose.tools.assert_raises(AttributeError, set_e2_connection)
#    nose.tools.assert_raises(AttributeError, set_e2_project)
#    nose.tools.assert_raises(AttributeError, set_e2_id)
#    nose.tools.assert_raises(AttributeError, set_e2_pyxnat_experiment)
#    nose.tools.assert_raises(AttributeError, set_e2_xml)
#    nose.tools.assert_raises(AttributeError, set_e2_subject)
#    nose.tools.assert_raises(AttributeError, set_e2_label)
#    nose.tools.assert_raises(AttributeError, set_e2_primary_subject)
#    nose.tools.assert_raises(AttributeError, set_e2_primary_label)
#    nose.tools.assert_raises(AttributeError, set_e2_scans)
#    nose.tools.assert_raises(AttributeError, set_e2_reconstructions)
#    nose.tools.assert_raises(AttributeError, set_e2_assessments)
#    nose.tools.assert_raises(AttributeError, set_e2_resources)
#    nose.tools.assert_raises(AttributeError, set_e2_workflows)

def test_scans():
    assert isinstance(e.scans, _Dictionary)
    assert 'mpr-1' in e.scans
    assert isinstance(e.scans['mpr-1'], _Scan)
    assert 'xxxxxxxx' not in e.scans
    assert len(e.scans) == 4

def test_reconstructions():
    assert isinstance(e.reconstructions, _Dictionary)
    assert 'OAS1_0054_MR1_RECON1' in e.reconstructions
    assert isinstance(e.reconstructions['OAS1_0054_MR1_RECON1'], _Reconstruction)
    assert 'xxxxxxxx' not in e.reconstructions
    assert len(e.reconstructions) == 1

def test_assessments():
    assert isinstance(e.assessments, _Dictionary)
    assert 'OAS1_0054_MR1_ASEG' in e.assessments
    assert isinstance(e.assessments['OAS1_0054_MR1_ASEG'], _Assessment)
    assert 'xxxxxxxx' not in e.assessments
    assert len(e.assessments) == 4

def test_workflows():
    assert isinstance(workflow_experiment.workflows, _Dictionary)
    assert 475 in workflow_experiment.workflows
    assert isinstance(workflow_experiment.workflows[475], _Workflow)
    assert len(e.workflows) == 0

def teardown():
    c.close()

# eof
