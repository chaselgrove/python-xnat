import nose.tools
import pyxnat.core.resources
from .. import Connection

def set_a2_connection():
    a2.connection = ''

def set_a2_project():
    a2.project = ''

def set_a2_subject():
    a2.subject = ''

def set_a2_experiment():
    a2.experiment = ''

def set_a2_id():
    a2.id = ''

def set_a2_label():
    a2.label = ''

def set_a2_pyxnat_assessment():
    a2.pyxnat_assessment = ''

def set_a2_xml():
    a2.xml = ''

def set_a2_in_resources():
    a2.in_resources = ''

def set_a2_out_resources():
    a2.out_resources = ''

def setup():
    global connection, project, subject, experiment, assessment
    global a2
    connection = Connection('https://central.xnat.org', 
                            'nosetests', 
                            'nosetests')
    project = connection.projects['PALS']
    subject = project.subjects['Human_Buckner_Case01']
    experiment = subject.experiments['Human_Buckner_Case01']
    assessment = experiment.assessments['OAS1_0054_MR1_ASEG']
    raise NotImplementedError, 'need a2 and delete'
    a2 = None

def test_attributes():
    assert assessment.connection is connection
    assert assessment.project is project
    assert assessment.subject is subject
    assert assessment.experiment is experiment
    assert assessment.label == 'OAS1_0054_MR1_ASEG'
    assert assessment.id == 'OAS1_0054_MR1_ASEG'
    assert isinstance(assessment.pyxnat_assessment, pyxnat.core.resources.Assessor)
    assert isinstance(assessment.xml, str)
    assert assessment.xml.startswith('<?xml version="1.0" encoding="UTF-8"?>\n<fs:ASEGRegionAnalysis ID="OAS1_0054_MR1_ASEG"')
    assert assessment.xml.endswith('</fs:ASEGRegionAnalysis>\n')

def test_read_only():
    nose.tools.assert_raises(AttributeError, set_a2_connection)
    nose.tools.assert_raises(AttributeError, set_a2_project)
    nose.tools.assert_raises(AttributeError, set_a2_subject)
    nose.tools.assert_raises(AttributeError, set_a2_experiment)
    nose.tools.assert_raises(AttributeError, set_a2_id)
    nose.tools.assert_raises(AttributeError, set_a2_label)
    nose.tools.assert_raises(AttributeError, set_a2_pyxnat_assessment)
    nose.tools.assert_raises(AttributeError, set_a2_xml)
    nose.tools.assert_raises(AttributeError, set_a2_in_resources)
    nose.tools.assert_raises(AttributeError, set_a2_out_resources)

def teardown():
    connection.close()

# eof
