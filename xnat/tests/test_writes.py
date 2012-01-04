import nose.tools
import uuid
from .. import Connection

def set_subject_connection():
    subject.connection = ''

def set_subject_id():
    subject.id = ''

def set_subject_project():
    subject.project = ''

def set_subject_label():
    subject.label = ''

def set_subject_pyxnat_subject():
    subject.pyxnat_subject = ''

def set_subject_xml():
    subject.xml = ''

def set_subject_primary_project():
    subject.primary_project = ''

def set_subject_primary_label():
    subject.primary_label = ''

def set_subject_projects():
    subject.projects = ''

def set_subject_experiments():
    subject.experiments = ''

def set_subject_experiments_by_id():
    subject.experiments_by_id = ''

def set_subject_resources():
    subject.resources = ''

def setup():
    global c, subject
    new_subject_label = uuid.uuid1().hex
    c = Connection('https://central.xnat.org', 'nosetests', 'nosetests')
    project = c.projects['nosetests2']
    subject = project.create_subject(new_subject_label)

def test_subject_read_only():
    nose.tools.assert_raises(AttributeError, set_subject_connection)
    nose.tools.assert_raises(AttributeError, set_subject_id)
    nose.tools.assert_raises(AttributeError, set_subject_project)
    nose.tools.assert_raises(AttributeError, set_subject_label)
    nose.tools.assert_raises(AttributeError, set_subject_pyxnat_subject)
    nose.tools.assert_raises(AttributeError, set_subject_xml)
    nose.tools.assert_raises(AttributeError, set_subject_primary_project)
    nose.tools.assert_raises(AttributeError, set_subject_primary_label)
    nose.tools.assert_raises(AttributeError, set_subject_projects)
    nose.tools.assert_raises(AttributeError, set_subject_experiments)
    nose.tools.assert_raises(AttributeError, set_subject_experiments_by_id)
    nose.tools.assert_raises(AttributeError, set_subject_resources)

def teardown():
    subject.pyxnat_subject.delete()
    c.close()

# eof
