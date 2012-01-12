import uuid
import nose.tools
import pyxnat.core.resources
from .. import Connection, _Subject, _Experiment, DoesNotExistError, _Scan, _ScanResource

scan_id = '1'
scan_id_2 = '2'
scan_resource_label = 'srid'

def setup():
    global c, project, new_subject_label
    c = Connection('https://central.xnat.org', 'nosetests', 'nosetests')
    project = c.projects['nosetests2']
    new_subject_label = uuid.uuid1().hex

def test_create_subject():
    global new_subject
    assert new_subject_label not in project.subjects
    new_subject = project.create_subject(new_subject_label)
    assert isinstance(new_subject, _Subject)
    assert new_subject.label == new_subject_label
    nose.tools.assert_raises(ValueError, lambda: project.create_subject(new_subject_label))

def test_create_experiment():
    global new_experiment
    new_experiment_label = uuid.uuid1().hex
    assert new_experiment_label not in new_subject.experiments
    new_experiment = new_subject.create_experiment(new_experiment_label)
    assert isinstance(new_experiment, _Experiment)
    assert new_experiment.label == new_experiment_label
    nose.tools.assert_raises(ValueError, lambda: new_subject.create_experiment(new_experiment_label))

def test_create_scan():
    global new_scan
    assert scan_id not in new_experiment.scans
    new_scan = new_experiment.create_scan(scan_id)
    assert isinstance(new_scan, _Scan)
    assert new_scan.id == scan_id
    nose.tools.assert_raises(ValueError, lambda: new_experiment.create_scan(scan_id))

def test_create_scan_resource():
    assert scan_resource_label not in new_scan.resources
    resource = new_scan.create_resource(scan_resource_label)
    assert isinstance(resource, _ScanResource)
    assert resource.label == scan_resource_label
    assert scan_resource_label in new_scan.resources
    nose.tools.assert_raises(ValueError, lambda: new_scan.create_resource(scan_resource_label))

def test_create_no_experiment():
    new_scan_label_2 = '2'
    new_experiment.pyxnat_experiment.delete()
    nose.tools.assert_raises(DoesNotExistError, lambda: new_experiment.create_scan(new_scan_label_2))
    nose.tools.assert_raises(DoesNotExistError, lambda: new_scan.create_resource(scan_resource_label))

def test_create_no_subject():
    new_experiment_label_2 = uuid.uuid1().hex
    new_scan_label_2 = '2'
    new_subject.pyxnat_subject.delete()
    nose.tools.assert_raises(DoesNotExistError, lambda: new_subject.create_experiment(new_experiment_label_2))
    nose.tools.assert_raises(DoesNotExistError, lambda: new_experiment.create_scan(new_scan_label_2))

def teardown():
    c.close()

# eof
