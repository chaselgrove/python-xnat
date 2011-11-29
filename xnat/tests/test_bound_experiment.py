import pyxnat.core.resources
from .. import Connection

def setup():
    global c, s, e
    c = Connection('https://central.xnat.org/', 'nosetests', 'nosetests')
    s = c.projects['CENTRAL_OASIS_LONG'].subjects['OAS2_0010']
    e = s.experiments['OAS2_0010_MR1']

def test_attributes():
    assert e.connection is c
    assert e.id == 'CENTRAL_E00106'
    assert isinstance(e.pyxnat_experiment, pyxnat.core.resources.Experiment)
    assert isinstance(e.xml, str)
    e.xml.startswith('<xnat:MRSession ID="CENTRAL_E00106"')
    e.xml.endswith('</xnat:MRSession>\n')
    assert e.primary_subject == s
    assert e.primary_label == 'OAS2_0010_MR1'
    assert e.subject == s
    assert e.label == 'OAS2_0010_MR1'

def teardown():
    c.close()

# eof
