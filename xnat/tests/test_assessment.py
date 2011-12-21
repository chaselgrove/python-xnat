import pyxnat.core.resources
from .. import Connection

def setup():
    global connection, project, subject, experiment, assessment
    connection = Connection('https://central.xnat.org', 
                            'nosetests', 
                            'nosetests')
    project = connection.projects['PALS']
    subject = project.subjects['Human_Buckner_Case01']
    experiment = subject.experiments['Human_Buckner_Case01']
    assessment = experiment.assessments['OAS1_0054_MR1_ASEG']

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

def teardown():
    connection.close()

# eof
