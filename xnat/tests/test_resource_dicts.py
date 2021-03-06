import nose.tools
import pyxnat.core.resources
from .. import Connection, _Subject, _ProjectResource, _SubjectResource, _ExperimentResource, _ScanResource, _ReconstructionInResource, _ReconstructionOutResource, _AssessmentInResource, _AssessmentOutResource, _Dictionary

def setup():
    global c, project, subject, experiment, scan, assessment, reconstruction
    c = Connection('https://central.xnat.org', 'nosetests', 'nosetests')
    project = c.projects['nosetests']
    subject = c.projects['nosetests'].subjects['resource_test']
    experiment = c.projects['nosetests'].subjects['resource_test'].experiments['resource_test_MR']
    scan = c.projects['PALS'].subjects['Human_Buckner_Case01'].experiments['Human_Buckner_Case01'].scans['mpr-1']
    reconstruction = c.projects['nosetests'].subjects['resource_test'].experiments['resource_test_MR'].reconstructions['recon']
    assessment = c.projects['nosetests'].subjects['resource_test'].experiments['resource_test_MR'].assessments['assessment']

def test_project_resources():
    assert isinstance(project.resources, _Dictionary)
    assert 'hx' in project.resources
    assert isinstance(project.resources['hx'], _ProjectResource)
    assert len(project.resources) == 1

def test_subject_resources():
    assert isinstance(subject.resources, _Dictionary)
    assert 'hx' in subject.resources
    assert isinstance(subject.resources['hx'], _SubjectResource)
    assert len(subject.resources) == 1

def test_experiment_resources():
    assert isinstance(experiment.resources, _Dictionary)
    assert 'hx' in experiment.resources
    assert isinstance(experiment.resources['hx'], _ExperimentResource)
    assert len(subject.resources) == 1

def test_scan_resources():
    assert isinstance(scan.resources, _Dictionary)
    assert 'ANALYZE' in scan.resources
    assert isinstance(scan.resources['ANALYZE'], _ScanResource)
    assert len(scan.resources) == 1

def test_reconstruction_resources():
    assert isinstance(reconstruction.in_resources, _Dictionary)
    assert isinstance(reconstruction.out_resources, _Dictionary)
    assert 'tir' in reconstruction.in_resources
    assert 'tor' in reconstruction.out_resources
    assert isinstance(reconstruction.in_resources['tir'], _ReconstructionInResource)
    assert isinstance(reconstruction.out_resources['tor'], _ReconstructionOutResource)
    assert len(reconstruction.in_resources) == 1
    assert len(reconstruction.out_resources) == 1

def test_assessment_resources():
    assert isinstance(assessment.in_resources, _Dictionary)
    assert isinstance(assessment.out_resources, _Dictionary)
    assert 'tia' in assessment.in_resources
    assert 'toa' in assessment.out_resources
    assert isinstance(assessment.in_resources['tia'], _AssessmentInResource)
    assert isinstance(assessment.out_resources['toa'], _AssessmentOutResource)
    assert len(assessment.in_resources) == 1
    assert len(assessment.out_resources) == 1

def teardown():
    c.close()

# eof
