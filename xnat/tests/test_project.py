import nose.tools
import pyxnat.core.resources
from .. import Connection, _Subject

def setup():
    global c, p, description, name, secondary_id
    c = Connection('https://central.xnat.org', 'nosetests', 'nosetests')
    p = c.projects['CENTRAL_OASIS_LONG']
    description = p.pyxnat_project.attrs.get('description')
    name = p.pyxnat_project.attrs.get('name')
    secondary_id = p.pyxnat_project.attrs.get('secondary_ID')

def test_attributes():
    assert p.id == 'CENTRAL_OASIS_LONG'
    assert p.connection is c
    assert isinstance(p.pyxnat_project, pyxnat.core.resources.Project)
    assert p.name == name
    assert p.description == description
    assert p.secondary_id == secondary_id
    assert isinstance(p.pyxnat_project, pyxnat.core.resources.Project)
    assert isinstance(p.xml, str)
    assert p.xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert p.xml.endswith('</xnat:Project>\n')

def test_subjects():
    assert isinstance(p.subjects, dict)
    # label of a subject
    assert 'OAS2_0001' in p.subjects
    # ID of the same subject
    assert 'CENTRAL_S00081' not in p.subjects
    assert isinstance(p.subjects['OAS2_0001'], _Subject)
    assert isinstance(p.subjects_by_id, dict)
    assert 'CENTRAL_S00088' in p.subjects_by_id
    assert 'OAS2_0010' not in p.subjects_by_id
    assert isinstance(p.subjects_by_id['CENTRAL_S00088'], _Subject)
    assert p.subjects_by_id['CENTRAL_S00088'].id == 'CENTRAL_S00088'
    assert p.subjects_by_id['CENTRAL_S00088'].label == 'OAS2_0010'

def teardown():
    c.close()

# eof
