import pyxnat.core.resources
from .. import Connection

def setup():
    global c, s, e, ps
    c = Connection('https://central.xnat.org', 'nosetests', 'nosetests')
    s = c.projects['PALS'].subjects['Human_Buckner_Case01']
    e = s.experiments['Human_Buckner_Case01']
    ps = c.projects['CENTRAL_OASIS_CS'].subjects['OAS1_0054']

def test_attributes():
    assert e.connection is c
    assert e.id == 'OAS1_0054_MR1'
    assert isinstance(e.pyxnat_experiment, pyxnat.core.resources.Experiment)
    assert isinstance(e.xml, str)
    e.xml.startswith('<xnat:MRSession ID="OAS1_0054_MR1"')
    e.xml.endswith('</xnat:MRSession>\n')
    assert e.subject is s
    assert e.label == 'Human_Buckner_Case01'
    assert e.primary_subject is ps
    assert e.primary_label == 'OAS1_0054_MR1'

def teardown():
    c.close()

# eof
