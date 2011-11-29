import nose.tools
import pyxnat.core.resources
from .. import Connection

def setup():
    global c, e
    c = Connection('https://central.xnat.org/', 'nosetests', 'nosetests')
    e = c.get_subject('OAS1_0010').experiments['OAS1_0010_MR1']

def test_attributes():
    assert e.connection is c
    assert e.id == 'OAS1_0010_MR1'
    assert isinstance(e.pyxnat_experiment, pyxnat.core.resources.Experiment)
    assert isinstance(e.xml, str)
    e.xml.startswith('<xnat:MRSession ID="OAS1_0010_MR1"')
    e.xml.endswith('</xnat:MRSession>\n')
    assert e.primary_subject == c.get_subject('OAS1_0010')
    assert e.primary_label == 'OAS1_0010_MR1'
    nose.tools.assert_raises(AttributeError, lambda: e.subject)
    nose.tools.assert_raises(AttributeError, lambda: e.label)

def teardown():
    c.close()

# eof
