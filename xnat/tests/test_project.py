import nose.tools
import pyxnat.core.resources
from .. import Connection, _BoundSubject

def setup():
    global c, p, label, description, name, secondary_id
    c = Connection('https://central.xnat.org', 'nosetests', 'nosetests')
    p = c.projects['CENTRAL_OASIS_LONG']
    label = p.pyxnat_project.label()
    description = p.pyxnat_project.attrs.get('description')
    name = p.pyxnat_project.attrs.get('name')
    secondary_id = p.pyxnat_project.attrs.get('secondary_ID')

def test_attributes():
    assert p.id == 'CENTRAL_OASIS_LONG'
    assert p.connection is c
    assert isinstance(p.pyxnat_project, pyxnat.core.resources.Project)
    assert p.name == name
    assert p.label == label
    assert p.description == description
    assert p.secondary_id == secondary_id
    assert isinstance(p.pyxnat_project, pyxnat.core.resources.Project)
    assert isinstance(p.xml, str)
    assert p.xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert p.xml.endswith('</xnat:Project>\n')

def test_subjects():
    assert isinstance(p.subjects, dict)
    assert 'OAS2_0010' in p.subjects
    assert isinstance(p.subjects['OAS2_0010'], _BoundSubject)
    assert 'xxxxxxxx' not in p.subjects
    assert 'CENTRAL_S00088' not in p.subjects

def teardown():
    c.close()

# eof
