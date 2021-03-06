import uuid
import nose.tools
import pyxnat.core.resources
from .. import Connection, _Subject, _Dictionary

def set_p2_id():
    p2.id = ''

def set_p2_connection():
    p2.connection = ''

def set_p2_pyxnat_project():
    p2.pyxnat_project = ''

def set_p2_name():
    p2.name = ''

def set_p2_description():
    p2.description = ''

def set_p2_secondary_id():
    p2.secondary_id = ''

def set_p2_xml():
    p2.xml = ''

def set_p2_subjects():
    p2.subjects = ''

def set_p2_subjects_by_id():
    p2.subjects_by_id = ''

def set_p2_resources():
    p2.resources = ''

def setup():
    global c, p, p2, description, name, secondary_id, new_subject_label
    c = Connection('https://central.xnat.org', 'nosetests', 'nosetests')
    p = c.projects['CENTRAL_OASIS_LONG']
    p2 = c.projects['nosetests2']
    description = p.pyxnat_project.attrs.get('description')
    name = p.pyxnat_project.attrs.get('name')
    secondary_id = p.pyxnat_project.attrs.get('secondary_ID')
    new_subject_label = uuid.uuid1().hex

def test_attributes():
    assert p.id == 'CENTRAL_OASIS_LONG'
    assert p.connection is c
    assert isinstance(p.pyxnat_project, pyxnat.core.resources.Project)
    assert p.name == name
    assert p.description == description
    assert p.secondary_id == secondary_id
    assert isinstance(p.xml, str)
    assert p.xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert p.xml.endswith('</xnat:Project>\n')

def test_read_only():
    nose.tools.assert_raises(AttributeError, set_p2_id)
    nose.tools.assert_raises(AttributeError, set_p2_connection)
    nose.tools.assert_raises(AttributeError, set_p2_pyxnat_project)
    nose.tools.assert_raises(AttributeError, set_p2_name)
    nose.tools.assert_raises(AttributeError, set_p2_description)
    nose.tools.assert_raises(AttributeError, set_p2_secondary_id)
    nose.tools.assert_raises(AttributeError, set_p2_xml)
    nose.tools.assert_raises(AttributeError, set_p2_subjects)
    nose.tools.assert_raises(AttributeError, set_p2_subjects_by_id)
    nose.tools.assert_raises(AttributeError, set_p2_resources)

def test_subjects():
    assert isinstance(p.subjects, _Dictionary)
    # label of a subject
    assert 'OAS2_0001' in p.subjects
    # ID of the same subject
    assert 'CENTRAL_S00081' not in p.subjects
    assert isinstance(p.subjects['OAS2_0001'], _Subject)
    assert isinstance(p.subjects_by_id, _Dictionary)
    assert 'CENTRAL_S00088' in p.subjects_by_id
    assert 'OAS2_0010' not in p.subjects_by_id
    assert isinstance(p.subjects_by_id['CENTRAL_S00088'], _Subject)
    assert p.subjects_by_id['CENTRAL_S00088'].id == 'CENTRAL_S00088'
    assert p.subjects_by_id['CENTRAL_S00088'].label == 'OAS2_0010'

def test_create_subject():
    assert new_subject_label not in p2.subjects
    new_subject = p2.create_subject(new_subject_label)
    assert isinstance(new_subject, _Subject)
    assert new_subject.label == new_subject_label
    nose.tools.assert_raises(ValueError, lambda: p2.create_subject(new_subject_label))
    new_subject.pyxnat_subject.delete()

def teardown():
    c.close()

# eof
